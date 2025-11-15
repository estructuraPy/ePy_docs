# Cómo Agregar Referencias en ePy_docs

## Dos Tipos de Referencias

ePy_docs maneja **dos tipos diferentes** de referencias:

### 1. Referencias Cruzadas Internas (`add_reference_to_element`)
Para referenciar **elementos dentro del mismo documento** (tablas, figuras, ecuaciones).

### 2. Citas Bibliográficas (`add_reference_citation` o sintaxis `@key`)
Para citar **fuentes externas** desde un archivo `.bib`.

---

## Parte 1: Referencias Cruzadas Internas

### Método: `add_reference_to_element()`

**Uso**: Referenciar tablas, figuras o ecuaciones que creaste en el mismo documento.

#### Ejemplo Completo:

```python
writer = DocumentWriter("paper", layout_style="academic")

# Crear una figura con label
fig, ax = plt.subplots()
ax.plot([1, 2, 3], [1, 4, 9])
writer.add_plot(fig, title="Datos Experimentales", label="fig-experimental")

# Crear una tabla con label
df = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
writer.add_table(df, title="Resultados", label="tbl-results")

# Crear una ecuación con label
writer.add_equation("E = mc^2", caption="Energía", label="eq-einstein")

# Más adelante, referenciar estos elementos
writer.add_text("Como se muestra en ")
writer.add_reference_to_element("figure", "fig-experimental")
writer.add_text(", los datos experimentales...")

writer.add_text("Los resultados de ")
writer.add_reference_to_element("table", "tbl-results")
writer.add_text(" indican que...")

writer.add_text("Según ")
writer.add_reference_to_element("equation", "eq-einstein")
writer.add_text(", la energía...")
```

**Resultado en el documento**:
- "Como se muestra en Figura 1, los datos experimentales..."
- "Los resultados de Tabla 1 indican que..."
- "Según Ecuación 1, la energía..."

---

## Parte 2: Citas Bibliográficas Externas

### Método 1: `add_reference_citation()` (Programático)

```python
writer.add_text("El código sísmico ")
writer.add_reference_citation("CSCR2010")
writer.add_text(" establece requisitos...")

# Con número de página
writer.add_reference_citation("ACI318", page="42")
```

### Método 2: Sintaxis `@key` en el Texto (Recomendado)

**Más simple y natural** - usa la sintaxis de Pandoc directamente en el texto:

```python
# Cita entre paréntesis
writer.add_text("El código sísmico [@CSCR2010] establece requisitos...")
# Resultado: "El código sísmico (CFIA, 2010) establece requisitos..."

# Cita narrativa (en el flujo del texto)
writer.add_text("Según @ACI318, el concreto debe cumplir...")
# Resultado: "Según American Concrete Institute (2019), el concreto debe cumplir..."

# Múltiples citas
writer.add_text("Los códigos [@CSCR2010; @ACI318; @ASCE7] establecen...")
# Resultado: "Los códigos (CFIA, 2010; ACI, 2019; ASCE, 2016) establecen..."
```

---

## Configurar Referencias Bibliográficas

### 1. Agregar Entradas al Archivo `references.bib`

Las referencias se deben agregar al archivo `.bib` en formato BibTeX. El archivo incluido con la librería está en:
```
src/ePy_docs/config/assets/bibliography/references.bib
```

### 2. Formato BibTeX para Diferentes Tipos de Referencias

#### Código o Estándar (@standard)
```bibtex
@standard{CSCR2010,
  title = {Código Sísmico de Costa Rica 2010},
  author = {{Colegio Federado de Ingenieros y Arquitectos}},
  institution = {Colegio Federado de Ingenieros y Arquitectos},
  publisher = {Editorial Tecnológica de Costa Rica},
  year = {2010},
  edition = {4ta},
  address = {San José, Costa Rica},
  language = {spa}
}
```

#### Libro (@book)
```bibtex
@book{ACI318_19,
  title = {Building Code Requirements for Structural Concrete (ACI 318-19)},
  author = {{American Concrete Institute}},
  organization = {American Concrete Institute},
  year = {2019},
  address = {Farmington Hills, MI},
  note = {An ACI Standard}
}
```

#### Norma Técnica (@standard o @techreport)
```bibtex
@standard{ASCE7_16,
  title = {Minimum Design Loads and Associated Criteria for Buildings and Other Structures},
  author = {{American Society of Civil Engineers}},
  organization = {American Society of Civil Engineers},
  year = {2016},
  address = {Reston, VA},
  note = {ASCE/SEI 7-16}
}
```

#### Artículo de Revista (@article)
```bibtex
@article{Smith2020,
  author = {Smith, John and Doe, Jane},
  title = {Seismic Analysis of Steel Structures},
  journal = {Journal of Structural Engineering},
  year = {2020},
  volume = {146},
  number = {3},
  pages = {04019210},
  doi = {10.1061/(ASCE)ST.1943-541X.0002532}
}
```

#### Tesis (@mastersthesis o @phdthesis)
```bibtex
@mastersthesis{Valverde2015,
  author = {Alonso Valverde-Ugalde},
  title = {Determinación experimental de la distribución de fuerzas en baldosas de concreto},
  school = {Universidad de Costa Rica},
  year = {2015},
  type = {Tesis de Maestría},
  address = {San José, Costa Rica}
}
```

### 3. Citar en el Texto

Una vez agregadas las entradas al `.bib`, se citan en el documento usando:

**Citas entre paréntesis:**
```python
writer.add_text("El código sísmico [@CSCR2010] establece requisitos...")
# Resultado: "El código sísmico (CFIA, 2010) establece requisitos..."
```

**Citas narrativas (en el flujo del texto):**
```python
writer.add_text("Según @ACI318_19, el concreto debe cumplir...")
# Resultado: "Según American Concrete Institute (2019), el concreto debe cumplir..."
```

**Múltiples citas:**
```python
writer.add_text("Los códigos de diseño [@CSCR2010; @ACI318_19; @ASCE7_16] establecen...")
# Resultado: "Los códigos de diseño (CFIA, 2010; ACI, 2019; ASCE, 2016) establecen..."
```

### 4. Generar el Documento

```python
from ePy_docs import DocumentWriter
from pathlib import Path

# Obtener ruta al archivo .bib incluido
package_root = Path(__file__).parent.parent / 'src' / 'ePy_docs'
bibliography = package_root / 'config' / 'assets' / 'bibliography' / 'references.bib'
csl_style = package_root / 'config' / 'assets' / 'csl' / 'ieee.csl'

# Crear documento
writer = DocumentWriter("paper", layout_style="academic")

# Agregar contenido con citas
writer.add_text("El diseño sísmico según @CSCR2010 requiere análisis...")
writer.add_text("Los requisitos de concreto [@ACI318_19] establecen...")

# Generar con bibliografía
result = writer.generate(
    pdf=True,
    html=True,
    bibliography_path=str(bibliography),
    csl_path=str(csl_style)
)
```

## Ejemplo de Referencias que Mencionaste

Para las referencias que intentabas agregar con `add_reference`, aquí está el formato correcto en `.bib`:

```bibtex
@standard{CSCR2010,
  title = {Código Sísmico de Costa Rica 2010},
  author = {{Colegio Federado de Ingenieros y Arquitectos de Costa Rica}},
  institution = {CFIA},
  publisher = {CFIA},
  year = {2010},
  edition = {4},
  address = {San José, Costa Rica}
}

@standard{ACI318,
  title = {Building Code Requirements for Structural Concrete (ACI 318-19)},
  author = {{American Concrete Institute}},
  organization = {American Concrete Institute},
  year = {2019},
  address = {Farmington Hills, MI},
  note = {An ACI Standard}
}

@standard{ASCE7,
  title = {Minimum Design Loads and Associated Criteria for Buildings and Other Structures (ASCE/SEI 7-16)},
  author = {{American Society of Civil Engineers}},
  organization = {ASCE},
  year = {2016},
  address = {Reston, VA}
}
```

Luego en tu código Python:
```python
writer.add_text("El código sísmico @CSCR2010 establece...")
writer.add_text("Los requisitos del concreto [@ACI318] indican...")
writer.add_text("Las cargas de diseño según @ASCE7 son...")
```

## Resumen Rápido

### Referencias Cruzadas Internas (dentro del documento):
```python
# 1. Crear elemento con label
writer.add_plot(fig, title="Mi Gráfico", label="fig-myplot")
writer.add_table(df, title="Mis Datos", label="tbl-data")
writer.add_equation("E=mc^2", label="eq-energy")

# 2. Referenciar después
writer.add_reference_to_element("figure", "fig-myplot")
writer.add_reference_to_element("table", "tbl-data")
writer.add_reference_to_element("equation", "eq-energy")
```

### Citas Bibliográficas (fuentes externas):
```python
# Método 1: Sintaxis @key (recomendado)
writer.add_text("El estudio [@Smith2020] demuestra...")
writer.add_text("Según @Jones2019, los resultados...")

# Método 2: Programático
writer.add_reference_citation("Smith2020")
writer.add_reference_citation("Jones2019", page="42")
```

## Ventajas de Este Enfoque

✅ **Estándar**: Usa BibTeX, el formato estándar académico  
✅ **Consistente**: El estilo CSL formatea todas las citas uniformemente  
✅ **Reutilizable**: El mismo `.bib` sirve para múltiples documentos  
✅ **Flexible**: Cambiar el estilo CSL reformatea todas las citas automáticamente  
✅ **Automático**: La lista de referencias se genera automáticamente al final

## Referencias Adicionales

- [BibTeX Format](http://www.bibtex.org/Format/)
- [BibTeX Entry Types](https://www.bibtex.com/e/entry-types/)
- [Citation Style Language](https://citationstyles.org/)
