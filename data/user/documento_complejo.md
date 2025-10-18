# Análisis Estructural Completo de Edificio Multifamiliar

**Proyecto:** Torre Residencial Vista Hermosa  
**Ubicación:** San José, Costa Rica  
**Fecha:** 18 de octubre de 2025  
**Ingeniero responsable:** Ing. María González, CFIA 12345

---

## 1. Introducción

Este documento presenta el análisis estructural completo del proyecto Torre Residencial Vista Hermosa, un edificio de 15 niveles con uso residencial ubicado en el distrito de Escazú, San José.

### 1.1 Objetivos del análisis

Los objetivos principales de este análisis son [@eurocode2; @aci318]:

1. Verificar la capacidad estructural bajo cargas gravitacionales
2. Evaluar el desempeño sísmico según CSCR-2010 [@cscr2010]
3. Diseñar elementos estructurales principales
4. Optimizar el uso de materiales

:::callout-important
## Consideraciones sísmicas

Costa Rica se encuentra en una zona de alta sismicidad. El diseño debe cumplir estrictamente con el CSCR-2010 [@cscr2010] y considerar los efectos de sitio.
:::

---

## 2. Características del Proyecto

### 2.1 Geometría

El edificio tiene las siguientes características geométricas:

| Parámetro | Valor | Unidad |
|-----------|-------|--------|
| Altura total | 45.0 | m |
| Número de niveles | 15 | - |
| Altura típica | 2.8 | m |
| Área de planta típica | 850 | m² |
| Área total construida | 12,750 | m² |

: Tabla 1: Características geométricas del edificio {#tbl-geometria}

### 2.2 Materiales

Se utilizarán los siguientes materiales estructurales:

: Tabla 2: Propiedades de materiales estructurales

| Material | Resistencia | Módulo Elástico | Densidad |
|----------|-------------|-----------------|----------|
| Concreto f'c | 28 MPa | 25,000 MPa | 2,400 kg/m³ |
| Acero fy | 420 MPa | 200,000 MPa | 7,850 kg/m³ |
| Mampostería | 15 MPa | 10,000 MPa | 1,800 kg/m³ |

Estos materiales cumplen con las especificaciones de [@aci318; @astm615].

![Diagrama de flujo del proceso de análisis](images/flow_diagram.png){#fig-flow width=80%}

---

## 3. Modelo Estructural

### 3.1 Sistema estructural

El sistema estructural consiste en un marco de concreto reforzado con las siguientes características:

- Columnas perimetrales: 60 cm × 60 cm
- Columnas interiores: 50 cm × 50 cm  
- Vigas principales: 40 cm × 60 cm
- Vigas secundarias: 30 cm × 50 cm
- Losa nervada: 25 cm espesor total

:::callout-note
El sistema de marcos de concreto reforzado fue seleccionado por su excelente comportamiento sísmico y facilidad constructiva.
:::

### 3.2 Cargas de diseño

Las cargas aplicadas al modelo se resumen en la siguiente tabla:

| Tipo de carga | Ubicación | Magnitud | Referencia |
|---------------|-----------|----------|------------|
| Carga muerta | Losa típica | 5.5 kN/m² | CSCR-2010 [@cscr2010] |
| Carga viva | Residencial | 2.0 kN/m² | CSCR-2010 [@cscr2010] |
| Carga viva | Pasillos | 3.0 kN/m² | CSCR-2010 [@cscr2010] |
| Carga viva | Balcones | 3.5 kN/m² | CSCR-2010 [@cscr2010] |
| Carga muerta | Mampostería | 3.0 kN/m² | Calculado |

: Tabla 3: Cargas gravitacionales aplicadas {#tbl-cargas}

![Modelo 3D del edificio en software de análisis](images/3d_model.png){#fig-model width=100%}

La @fig-model muestra el modelo tridimensional utilizado para el análisis. Se puede observar la distribución de columnas y el sistema de vigas.

---

## 4. Análisis Sísmico

### 4.1 Parámetros sísmicos

Según el CSCR-2010 [@cscr2010], se utilizaron los siguientes parámetros para la zona de estudio:

: Parámetros sísmicos de diseño

| Parámetro | Símbolo | Valor | Unidad |
|-----------|---------|-------|--------|
| Aceleración pico efectiva | a_ef | 0.44 | g |
| Factor de zona sísmica | Z | 0.4 | - |
| Tipo de suelo | - | S3 | - |
| Factor de sitio | S | 1.2 | - |
| Período de vibración | T₁ | 0.85 | s |
| Coeficiente sísmico | C | 0.18 | - |

### 4.2 Espectro de respuesta

El espectro de respuesta elástico se calculó según la ecuación del CSCR-2010:

$$
S_a(T) = \frac{2.5 \cdot a_{ef} \cdot S \cdot I}{R}
$$ {#eq-espectro}

Donde:
- $S_a(T)$ = Pseudo-aceleración espectral
- $a_{ef}$ = Aceleración pico efectiva  
- $S$ = Factor de sitio
- $I$ = Factor de importancia
- $R$ = Factor de reducción de respuesta

Para este proyecto: $I = 1.0$ (edificio normal), $R = 5.0$ (marco especial de concreto).

:::callout-warning
## Verificación de irregularidades

El edificio presenta irregularidad torsional menor. Se aplicó factor de amplificación $\Omega = 1.2$ en diseño de elementos verticales.
:::

![Espectro de respuesta elástico e inelástico](images/response_spectrum.png){#fig-spectrum width=90%}

---

## 5. Resultados del Análisis

### 5.1 Modos de vibración

Los primeros tres modos de vibración se presentan a continuación:

| Modo | Período (s) | Masa modal X (%) | Masa modal Y (%) | Tipo |
|------|-------------|------------------|------------------|------|
| 1 | 0.852 | 68.5 | 0.3 | Traslacional X |
| 2 | 0.801 | 0.2 | 72.3 | Traslacional Y |
| 3 | 0.645 | 0.5 | 0.4 | Torsional |
| 4 | 0.312 | 12.3 | 0.1 | Traslacional X |
| 5 | 0.298 | 0.1 | 11.8 | Traslacional Y |

: Tabla 4: Períodos y participación modal {#tbl-modos}

La suma de masa modal alcanza más del 90% en ambas direcciones con los primeros 5 modos, cumpliendo con los requisitos del CSCR-2010 [@cscr2010].

### 5.2 Derivas de piso

Las derivas máximas de entrepiso se muestran en la siguiente tabla:

: Derivas de entrepiso máximas

| Nivel | Deriva X (%) | Deriva Y (%) | Límite CSCR | Estado |
|-------|--------------|--------------|-------------|--------|
| Nivel 15 | 0.45 | 0.52 | 1.0 | ✓ OK |
| Nivel 12 | 0.62 | 0.68 | 1.0 | ✓ OK |
| Nivel 9 | 0.71 | 0.75 | 1.0 | ✓ OK |
| Nivel 6 | 0.68 | 0.71 | 1.0 | ✓ OK |
| Nivel 3 | 0.52 | 0.58 | 1.0 | ✓ OK |

Todas las derivas están por debajo del límite de 1.0% establecido para edificios de concreto reforzado.

![Gráfico de derivas por nivel](images/drift_chart.png){#fig-drift width=85%}

Como se observa en la @fig-drift, las derivas máximas ocurren en los niveles intermedios (niveles 8-10).

---

## 6. Diseño de Elementos

### 6.1 Columnas típicas

Las columnas críticas fueron diseñadas con los siguientes resultados:

| Elemento | Sección | P_u (kN) | M_ux (kN·m) | M_uy (kN·m) | Refuerzo | DCR |
|----------|---------|----------|-------------|-------------|----------|-----|
| C-1 (Nivel 1) | 60×60 | 2,850 | 185 | 165 | 16φ25 | 0.87 |
| C-2 (Nivel 1) | 50×50 | 1,950 | 142 | 128 | 12φ25 | 0.82 |
| C-1 (Nivel 8) | 60×60 | 1,450 | 225 | 198 | 16φ25 | 0.78 |
| C-2 (Nivel 8) | 50×50 | 985 | 165 | 152 | 12φ25 | 0.75 |

: Tabla 5: Diseño de columnas críticas {#tbl-columnas}

Donde:
- DCR = Demand-Capacity Ratio (Relación demanda-capacidad)
- P_u = Carga axial última
- M_ux, M_uy = Momentos últimos en X e Y

:::callout-tip
## Optimización de refuerzo

Se utilizó cuantía de acero entre 1.5% y 2.2%, dentro del rango óptimo económico de 1.0% a 4.0% según [@park1975].
:::

### 6.2 Vigas principales

: Diseño de vigas principales

| Viga | Ubicación | M_u (kN·m) | V_u (kN) | Refuerzo superior | Refuerzo inferior |
|------|-----------|------------|----------|-------------------|-------------------|
| V-1 | Eje A-B | 285 | 165 | 4φ25 | 4φ20 |
| V-2 | Eje 1-2 | 245 | 148 | 4φ25 | 3φ20 |
| V-3 | Eje B-C | 268 | 158 | 4φ25 | 4φ20 |

Todas las vigas cumplen con requisitos de flexión, corte y detallado sísmico según ACI 318-19 [@aci318].

![Detalle de refuerzo típico de viga](images/beam_detail.png){#fig-beam width=70%}

---

## 7. Verificación de Derivas

Como se mencionó en la sección 5.2, todas las derivas están dentro de los límites permitidos. La verificación se realizó mediante:

$$
\Delta_i \leq 0.01 \cdot h_i
$$ {#eq-deriva}

Donde $\Delta_i$ es la deriva de entrepiso y $h_i$ es la altura del entrepiso.

Ver @tbl-modos para períodos fundamentales y @tbl-cargas para cargas aplicadas.

---

## 8. Conclusiones

1. El sistema estructural propuesto (marco especial de concreto) es adecuado para las solicitaciones del proyecto
2. Todas las derivas de entrepiso cumplen con los límites del CSCR-2010 [@cscr2010]
3. Los elementos diseñados tienen ratios demanda-capacidad menores a 0.90
4. Se recomienda verificación adicional de efectos P-Delta en análisis final

:::callout-important
## Recomendaciones

- Realizar análisis no-lineal estático (pushover) para verificación adicional
- Considerar efectos de interacción suelo-estructura
- Implementar sistema de monitoreo estructural durante construcción
:::

![Render del edificio terminado](images/building_render.png){#fig-render width=100%}

---

## Referencias

::: {#refs}
:::

---

## Apéndice A: Datos del modelo

Los archivos del modelo estructural están disponibles en:
- Modelo Robot Structural: `data/robot/modelo_completo.rtd`
- Resultados de análisis: `data/robot/resultados_analisis.xlsx`
- Planos estructurales: `data/drawings/estructural_*.dwg`

**Fin del documento**
