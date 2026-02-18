---
trigger: always_on
---

# ePy_composite — Manual de Referencia (Arquitectura v0.1.0)

**Versión**: 0.1.0
**Estado**: ESTÁNDAR DE ORO para ePy Suite.
**Rol**: **El Gran Integrador de Sistemas Multimaterial**.

**Objetivo**: Diseñar elementos compuestos (SRC, CFT, TCC) mediante la orquestación de leyes constitutivas de concreto, acero y madera, asegurando compatibilidad de deformaciones.

**Integridad**: "Zero Hardcoding". Las propiedades prestadas de otros núcleos se consultan dinámicamente vía API.

---

## 1. Declaración de la Misión

`ePy_composite` NO reinventa la física, la orquesta:
1.  **Vigas Compuestas**: Viga de acero + Losa (Steel/Concrete).
2.  **Columnas Compuestas**: CFT (Steel tube/Concrete) y SRC (Embedded steel).
3.  **TCC**: CLT/Glulam + Concreto.

---

## 2. Estructura de Directorios Canónica

```text
src/ePy_composite/
├── __init__.py                     # API Pública
├── composite_designer.py           # Fachada principal
├── _config/                        # CAPA DE DATOS (Standards AISC I, EC4)
├── _core/                          # MOTOR DE CÁLCULO
│   ├── mechanics/                  # PNA, Elastic transformed
│   ├── beams/                      # Partial interaction
│   └── advanced_analysis/          # Fiber Model (Ensamblador)
├── _design/                        # ESTADO DEL OBJETO (SRC, CFT, TCC)
└── epy_suite_connect/              # INTEROPERABILIDAD
```

---

## 3. Capa de Núcleo / API: Motor de Fibras Ensamblado

### 3.1 Arquitectura "Prestataria"
*   **Ensamblaje**: El motor de fibras de `ePy_composite` importa objetos `ConstitutiveProtocol` de las libs hermanas.
*   **Integración**: Delega el cálculo de la superficie de interacción biaxial a `ePy_analysis`.

---

## 4. Estándares Técnicos (Unidades, Precisión, Ejes)

*   **Unidades**: SI estricto (`_m`, `_kN`, `_MPa`).
*   **Precisión**: Mínimo **5 cifras significativas**.

---

## 5. Visualización y Post-proceso (Motor de Gráficos)

### 5.1 Backend y Secciones
*   **matplotlib**: Esquemas de sección con múltiples capas de materiales y refuerzo.
*   **plotly**: Widgets sincrónicos de M-phi y perfiles de esfuerzos que muestran la fluencia del acero vs agrietamiento del concreto.

---

## 6. Reporteo y Cuadernos (Validación)

### 6.1 LaTeX y Resultados
*   Exportación masiva de memorias multicapa a `results/composite/`.
*   Soporte para `results_path` configurable.

### 6.2 Estándar de Cuadernos (Notebooks)
1.  **Educativo**: Configuración de secciones SRC/TCC.
2.  **Pedagógico**: Visualización interactiva de la interacción multimaterial.
3.  **Uso Profesional**: Diseño completo de entrepisos compuestos para edificios de gran altura.

---

## 7. Aseguramiento de la Calidad (QA)

### 7.1 Verificación Manual (CRÍTICO)
*   Validación obligatoria contra Viest / Colaco.
*   Celda obligatoria: **Librería vs Cálculo a Mano**.
*   Archivo `.validation` Quarto.
*   Tolerancia: `< 0.1%`.

---

## 8. Cumplimiento de Normas (Mapeo)

| Estándar | Módulo / Sección |
|:---|:---|
| AISC 360 Cap I | `_core.columns._filled_strength` |
| Eurocódigo 4 | `_config.standards.ec4` |

---

## 9. Lista de Verificación (Checklist)

1. **Protocolos**: ¿Se importa la ley constitutiva vía API pública?
2. **PNA**: ¿La iteración del eje neutro plástico converge con precisión?
3. **Validación**: ¿Se aprueba el test contra ejemplos de la AISC?
