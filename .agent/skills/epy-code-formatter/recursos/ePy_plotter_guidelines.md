---
trigger: always_on
---

# ePy_plotter — Manual de Referencia (Arquitectura v0.1.0)

**Versión**: 0.1.0
**Estado**: ESTÁNDAR DE ORO para ePy Suite.
**Rol**: **Centro de Autoría BIM, Detallado e Interoperabilidad**.

**Objetivo**: CERRAR la brecha entre el cálculo estructural y la construcción mediante la generación de esquemas de alta fidelidad y modelos IFC4/IFC5.

**Filosofía**: "La Geometría Primero".

---

## 1. Declaración de la Misión

`ePy_plotter` actúa como la fuente de verdad geométrica:
1.  **Detallado de Alta Fidelidad**: Genera planos 2D (planta, sección, alzado) realistas.
2.  **Interoperabilidad BIM**: Lectura/Escritura nativa de IFC (ISO 16739).

---

## 2. Estructura de Directorios Canónica

```text
src/ePy_plotter/
├── __init__.py                     # API Pública
├── plotter.py                      # Fachada principal
├── ifc_converter.py                # Conversor BIM
├── _config/                        # Estilos (Hatches, Fonts, Sheets)
├── _backend/                       # Motores (Matplotlib, DXF, IFC)
├── _detailing/                     # Lógica por material (Concrete, Steel, etc.)
└── _blender/                       # Add-on y Vínculo en vivo
```

---

## 3. Capa de Núcleo / API: El Protocolo del Plotter

### 3.1 Contrato de Datos
`ePy_plotter` recibe diccionarios `detailing_dict` de las libs de material y los convierte en entidades gráficas:
*   **Validación**: Verifica si el refuerzo cabe en la sección (clear cover).
*   **Conflictos**: Detecta colisiones en nudos viga-columna.

---

## 4. Estándares Técnicos (Unidades, Precisión, Ejes)

*   **Unidades**: SI estricto (`_m`, `_kN`, `_MPa`).
*   **Precisión**: Mínimo **5 cifras significativas**.

---

## 5. Visualización y Post-proceso (Motor de Gráficos)

### 5.1 Backend Universal y Multimaterial
*   **matplotlib**: Motor por defecto para esquemas 2D y PDF.
*   **Blender (Bonsai)**: Visualización 3D en vivo con mapas de calor y armaduras realistas.
*   **Alcance**: Multimaterial y multiforma (muros, perfiles, madera).

---

## 6. Reporteo y Láminas

### 6.1 Gestión de Dibujos
*   Generación de viewports y cajetines estandarizados.
*   Exportación masiva de resultados a `results/drawings/`.

---

## 7. Interoperabilidad (BIM)

### 7.1 Exportación IFC
*   Mapeo de objetos de alto LOD: `IfcReinforcingBar`, `IfcMechanicalFastener`, `IfcFastener`.

---

## 8. Aseguramiento de la Calidad (QA)

### 8.1 Verificación Manual (CRÍTICO)
*   Validación obligatoria de espaciamientos libres contra ACI/AISC.
*   Celda obligatoria en cuadernos: **Geometría vs Standard**.
*   Archivo `.validation` Quarto.
*   Tolerancia: `< 0.1%`.

---

## 9. Lista de Verificación (Checklist)

1. **Unidades**: ¿Están todas las dimensiones en metros?
2. **BIM**: ¿Cumplen las familias con la codificación de IFC4?
3. **Validación**: ¿Se realizó el chequeo de colisiones en los nudos?
