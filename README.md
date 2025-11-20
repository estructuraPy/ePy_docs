# ePy_docs - Engineering Document Generation Library# ePy_docs

Para más estilos de citación: https://github.com/citation-style-language/styles


[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)**Sistema de Generación de Documentación Técnica para Ingeniería**

[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

[![Version](https://img.shields.io/badge/version-0.2.0-orange)](https://github.com/estructuraPy/ePy_docs)[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**ePy_docs** is a Python library for generating professional engineering documentation (technical reports, structural analysis, academic papers) with support for HTML and PDF outputs via Quarto.

---

## ✨ Key Features

## 📋 Descripción

- 🎯 **Simple API**: Clean wrapper interface with zero business logic  

- 📊 **Smart Tables**: Automatic color coding, image generation, and formatting  ePy_docs es una librería Python para generar documentación técnica profesional en formatos HTML y PDF, diseñada específicamente para proyectos de ingeniería estructural, geotécnica e hidráulica.

- 📄 **Multi-format Output**: HTML and PDF via Quarto/XeLaTeX  

- 🎨 **Professional Layouts**: Pre-configured styles (classic, modern, academic)  ### ✨ Características Principales

- 🔧 **Configuration System**: `.epyson` (source) → `.epyx` (cache) → `.json` (output)  

- 🚫 **No File Sync**: Reads directly from installation directory  - **API Fluida**: Interfaz intuitiva con method chaining

- 📦 **Organized Structure**: Clean separation of API, config, internals, resources- **Multi-formato**: Generación simultánea de HTML y PDF

- **Layouts Profesionales**: 8 estilos predefinidos (academic, corporate, minimal, etc.)

## 📦 Installation- **Integración con ePy_units**: Manejo automático de unidades de ingeniería

- **Tablas Inteligentes**: Detección automática de categorías y colorización

```bash- **Callouts**: Notas, advertencias, tips con estilos predefinidos

pip install ePy_docs- **Configuración Centralizada**: Sistema `.epyson` para configuraciones versionables

```

---

**Requirements:**

- Python 3.10+## 📁 Estructura del Proyecto

- ePy_units (for unit conversions)

- pandas, matplotlib, reportlab```

- Quarto (for PDF generation)ePy_docs/

├── 📓 Notebooks (Ejemplos y demos)

## 🚀 Quick Start│   ├── demo_unified_api.ipynb        # Demo completo de la API

│   ├── test_01_basic_report.ipynb    # Test básico

```python│   ├── backup_report.ipynb           # Backup

from ePy_docs.api.writers import ReportWriter│   └── report_1_updated.ipynb        # Reporte actualizado

│

# Initialize writer with layout style├── 📂 03_geotech/                    # Ejemplos geotécnicos

writer = ReportWriter(layout_style='classic')│   └── annex.ipynb                   # Anexo geotécnico

│

# Add content├── 📂 data/                          # Datos de ejemplo

writer.add_h1("Structural Analysis Report")│   ├── configuration/                # Configuraciones (.epyson)

writer.add_text("This report presents the structural analysis results.")│   ├── robot/                        # Datos de Robot Structural

│   └── user/                         # Datos de usuario

# Add tables with smart formatting│

writer.add_table(├── 📂 src/ePy_docs/                  # Código fuente

    df=nodes_df,│   ├── api/                          # API pública

    title="Node Coordinates",│   │   └── writers.py                # ReportWriter, PaperWriter

    format_type="decimal"│   │

)│   ├── config/                       # Sistema de configuración

│   │   ├── loader.py                 # ConfigLoader (.epyson/.epyx/.json)

# Add callouts│   │   └── settings.py               # Settings globales

writer.add_note("All calculations follow ACI 318-19 code.")│   │

writer.add_warning("Check material properties before final design.")│   ├── internals/                    # Componentes internos

│   │   ├── content/                  # Generadores de contenido

# Generate HTML and PDF│   │   │   ├── text.py               # Procesamiento de texto

results = writer.generate(html=True, pdf=True)│   │   │   ├── tables.py             # Tablas y gráficos

│   │   │   ├── notes.py              # Callouts

print(f"✅ HTML: {results['html']}")│   │   │   └── images.py             # Imágenes

print(f"✅ PDF: {results['pdf']}")│   │   │

```│   │   ├── styling/                  # Sistema de estilos

│   │   │   ├── colors.py             # Paletas de colores

## 📁 Project Structure│   │   │   └── pages.py              # Configuración de páginas

│   │   │

```│   │   ├── code.py                   # Bloques de código

ePy_docs/│   │   ├── data.py                   # Manejo de datos

├── src/ePy_docs/│   │   ├── format.py                 # Formateo (superíndices, wrapping)

│   ├── api/                    # Public API (pure wrappers)│   │   ├── generator.py              # Generación de documentos

│   │   ├── __init__.py│   │   ├── html.py                   # Conversión HTML

│   │   └── writers.py          # ReportWriter (no logic)│   │   ├── layout.py                 # Coordinador de layouts

│   ├── config/                 # Configuration loaders│   │   ├── pdf.py                    # Generación PDF

│   │   ├── __init__.py│   │   ├── project_info.py           # Información de proyecto

│   │   ├── loader.py           # ConfigLoader (.epyson/.epyx/.json)│   │   ├── quarto.py                 # Integración Quarto

│   │   ├── config_manager.py│   │   ├── references.py             # Referencias bibliográficas

│   │   └── setup.py│   │   ├── setup.py                  # Setup de proyecto

│   ├── internals/              # Implementation logic│   │   └── styler.py                 # Estilos YAML

│   │   ├── styling/            # Styles, colors, layouts, pages│   │

│   │   ├── generation/         # Quarto, HTML, PDF, references│   ├── resources/                    # Recursos estáticos

│   │   ├── data_processing/    # DataFrames, data utilities│   │   ├── configs/                  # Archivos .epyson

│   │   └── formatting/         # Text, tables, notes, code, images│   │   │   ├── colors.epyson         # Configuración de colores

│   └── resources/              # Configuration files│   │   │   ├── format.epyson         # Configuración de formato

│       ├── configs/            # .epyson, .epyx, .json files│   │   │   ├── pages.epyson          # Configuración de páginas

│       └── styles/             # .csl bibliography styles│   │   │   ├── master.epyson         # Configuración central

├── data/                       # Example data│   │   │   ├── tables.epyson         # Configuración de tablas

│   ├── robot/                  # Structural analysis data (CSV)│   │   │   └── text.epyson           # Configuración de texto

│   └── user/                   # User projects and templates│   │   │

├── report_structural_example.ipynb  # Complete example notebook│   │   └── styles/                   # Estilos CSS/LaTeX

├── demo_unified_api.ipynb      # API demonstration│   │

├── pyproject.toml              # Package configuration│   └── generators/                   # Generadores especializados

├── LICENSE                     # MIT License│       ├── base.py                   # Generador base

└── README.md                   # This file│       ├── html.py                   # HTML generator

```│       ├── markdown.py               # Markdown generator

│       └── pdf.py                    # PDF generator

## 🎨 Configuration Strategy│

├── 📂 docs/                          # Documentación

ePy_docs uses a **three-tier configuration system** for performance and flexibility:│   ├── CODE_QUALITY_ANALYSIS.md      # Análisis de calidad

│   ├── NUEVA_ESTRUCTURA.md           # Nueva estructura

1. **`.epyson`** (source): Human-editable JSON configuration files  │   └── SESSION_SUMMARY.md            # Resumen de sesiones

2. **`.epyx`** (cache): Compiled/cached configurations (auto-generated)  │

3. **`.json`** (output): Runtime generated configurations├── .gitignore

├── .pylintrc                         # Configuración de pylint

**Loading Priority:** `.epyx` (if fresh) > `.epyson` > `.json`├── pyproject.toml                    # Configuración del proyecto

├── LICENSE

Configuration files are located in `resources/` next to the modules that use them. No file synchronization—reads directly from the installation directory.└── README.md

```

### Example Configuration (`colors.epyson`)

---

```json

{## 🚀 Instalación

  "primary": "#2E86AB",

  "secondary": "#A23B72",### Instalación en Desarrollo

  "accent": "#F18F01",

  "success": "#06A77D",```bash

  "warning": "#F8961E",# Clonar el repositorio

  "danger": "#D62828"git clone https://github.com/estructuraPy/ePy_docs.git

}cd ePy_docs

```

# Instalar en modo editable

## 📝 Usage Examplespip install -e .

```

### 1. Basic Report

### Dependencias

```python

from ePy_docs.api.writers import ReportWriter```toml

[dependencies]

writer = ReportWriter(layout_style='classic')python = "^3.10"

writer.add_h1("Project Title")pandas = "^2.0.0"

writer.add_h2("Introduction")matplotlib = "^3.7.0"

writer.add_text("Project description...")jinja2 = "^3.1.0"

results = writer.generate(html=True)pyyaml = "^6.0"

```ePy_units = "^0.1.0"  # Sistema de unidades

```

### 2. Structural Analysis Report

---

```python

import pandas as pd## 💡 Uso Básico

from ePy_docs.api.writers import ReportWriter

### Ejemplo Mínimo

# Load data

nodes_df = pd.read_csv('data/robot/nodes.csv', sep=';')```python

reactions_df = pd.read_csv('data/robot/reactions.csv', sep=';')from ePy_docs.api.writers import ReportWriter

import pandas as pd

# Create writer

writer = ReportWriter(layout_style='classic')# Crear writer

writer = ReportWriter(layout_style='academic')

# Add content

writer.add_h1("Structural Analysis")# Agregar contenido

writer.add_h2("Node Coordinates")writer.add_h1("Mi Reporte")

writer.add_table(nodes_df, title="Coordinates", format_type="decimal")

writer.add_content("Este es un reporte técnico.")



writer.add_h2("Support Reactions")# Agregar tabla

writer.add_colored_table(df = pd.DataFrame({

    reactions_df,    'Elemento': ['C1', 'C2', 'C3'],

    title="Reactions",    'Fuerza (kN)': [100, 150, 200]

    color_column='Magnitude',})

    colormap='RdYlGn'writer.add_table(df, title="Resultados")

)

# Generar outputs

# Generateresults = writer.generate(html=True, pdf=True)

results = writer.generate(html=True, pdf=True)

print(f"HTML: {results['html']}")

```
print(f"PDF: {results['pdf']}")

```

### 3. Using Callouts

### Ejemplo con Callouts

```python

writer.add_note("This is an informational note.", title="Note")```python

writer.add_tip("Pro tip: Use this feature for better results.", title="Tip")# Agregar diferentes tipos de callouts

writer.add_warning("Warning: Check this value.", title="⚠️ Warning")writer.add_note("Información importante", "Nota")

writer.add_error("Error: Invalid input detected.", title="❌ Error")writer.add_warning("Revisa los valores", "Advertencia")

```writer.add_tip("Usa el layout 'corporate' para presentaciones", "Consejo")

writer.add_success("Cálculo verificado correctamente", "Éxito")

## 🔧 API Reference```



### ReportWriter### Layouts Disponibles



**Main class for generating technical reports.**```python

layouts = [

```python    'academic',      # Estilo académico clásico

ReportWriter(layout_style: str = 'classic')    'corporate',     # Presentaciones corporativas

```    'minimal',       # Diseño minimalista

    'technical',     # Documentación técnica

**Methods:**    'modern',        # Diseño moderno

    'classic',       # Estilo clásico

- `add_h1(text)`, `add_h2(text)`, `add_h3(text)`: Add headings      'elegant',       # Diseño elegante

- `add_text(content)`: Add paragraph text      'professional'   # Estilo profesional

- `add_list(items, ordered=False)`: Add lists  ]

- `add_table(df, title, **kwargs)`: Add table with smart formatting  

- `add_colored_table(df, title, color_column, **kwargs)`: Add heatmap table  writer = ReportWriter(layout_style='corporate')
```

### Sistema de Columnas

El sistema soporta múltiples configuraciones de columnas para tablas y figuras:

```python
# Tabla de una columna (ancho depende del document_type)
writer.add_table(df, columns=1)

# Tabla de dos columnas (solo en layouts de 2+ columnas)
writer.add_table(df, columns=2)

# Tabla de ancho personalizado (1.5 columnas)
writer.add_table(df, columns=1.5)

# Anchos exactos en pulgadas para cada parte de tabla dividida
writer.add_table(df, columns=[2.0, 1.5, 3.0])
```

**Tipos de documento:**
- `paper`: 1 columna por defecto (académico)
- `report`: 1 columna por defecto (profesional)
- `book`: 1 columna (libro)
- `presentation`: 1 columna (slides)
- `notebook`: 1 columna (cuaderno)


- `add_equation(latex_code, caption, label)`: Add LaTeX equation  ```

- `add_note(content, title)`: Add note callout  

- `add_tip(content, title)`: Add tip callout  ---

- `add_warning(content, title)`: Add warning callout  

- `add_error(content, title)`: Add error callout  ## 🎨 Sistema de Configuración

- `generate(html=True, pdf=False)`: Generate documents

### Archivos .epyson

### ConfigLoader

Los archivos de configuración usan la extensión `.epyson` (ePy Source Object Notation):

**Configuration loader with caching.**

```

```python.epyson  → Configuración fuente (versionado en git)

from ePy_docs.config import load_config.epyx    → Cache intermedio (temporal, no versionado)

.json    → Salida procesada (generado, no versionado)

config = load_config('colors')  # Loads colors.epyson/.epyx/.json```

```

### Ejemplo de colors.epyson

## 🎯 Design Philosophy

```json

ePy_docs follows these architectural principles:{

  "palettes": {

1. **API Purity**: `api/` contains only **pure wrappers** with zero business logic      "default": {

2. **Clean Separation**: All logic lives in `internals/`, organized by theme        "primary": "#2E86AB",

3. **No File Sync**: Direct reads from installation directory (no `sync_files`)        "secondary": "#A23B72",

4. **Configuration Strategy**: `.epyson` (source) → `.epyx` (cache) → `.json` (output)        "success": "#06A77D",

5. **Grouped by Topic**: Modules organized by functionality (styling, generation, formatting)      "warning": "#F18F01",

      "danger": "#C73E1D"

## 📚 Examples    }

  },

See the included notebooks for complete examples:  "layout_styles": {

    "academic": {

- **`report_structural_example.ipynb`**: Complete structural analysis report        "typography": {

- **`demo_unified_api.ipynb`**: API feature demonstrations        "h1": "#2E86AB",

        "h2": "#2E86AB"

## 🤝 Contributing      }

    }

Contributions are welcome! Please:  }

}

1. Fork the repository  ```

2. Create a feature branch  

3. Make your changes  ---

4. Submit a pull request

## 🧪 Testing

## 📄 License

Los tests están integrados en notebooks de Jupyter:

MIT License - see [LICENSE](LICENSE) file for details.

```bash

## 🔗 Links# Abrir notebook de test

jupyter notebook test_01_basic_report.ipynb

- **GitHub**: [github.com/estructuraPy/ePy_docs](https://github.com/estructuraPy/ePy_docs)  

- **Documentation**: [Coming soon]  # O ejecutar demo completo

- **ePy_units**: [github.com/estructuraPy/ePy_units](https://github.com/estructuraPy/ePy_units)jupyter notebook demo_unified_api.ipynb

```

## 🙏 Acknowledgments

---

- Built with [Quarto](https://quarto.org/) for document generation  

- Uses [XeLaTeX](https://tug.org/xelatex/) for PDF rendering  ## 📚 Documentación

- Powered by [Pandoc](https://pandoc.org/) for format conversions

- **[Análisis de Calidad](docs/CODE_QUALITY_ANALYSIS.md)**: Revisión SOLID y mejores prácticas

---- **[Nueva Estructura](docs/NUEVA_ESTRUCTURA.md)**: Detalles de la reorganización

- **[Session Summary](docs/SESSION_SUMMARY.md)**: Resumen de sesiones de desarrollo

**Made with ❤️ by estructuraPy**

---

## 🛠️ Desarrollo

### Estructura de Código

- **API Pública** (`api/`): Interfaces de usuario (ReportWriter, PaperWriter)
- **Config** (`config/`): Sistema de configuración centralizado
- **Internals** (`internals/`): Lógica interna (no usar directamente)
- **Resources** (`resources/`): Archivos de configuración y estilos

### Principios de Diseño

1. **API Fluida**: Method chaining para mejor UX
2. **Configuración sobre Código**: Todo configurable vía `.epyson`
3. **Separación de Responsabilidades**: Cada módulo tiene un propósito único
4. **Extensibilidad**: Fácil agregar nuevos layouts y formatos

---

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

---

## 👥 Autores

- **estructuraPy** - Desarrollo inicial

---

## 🙏 Agradecimientos

- **ePy_units**: Sistema de unidades de ingeniería
- **Quarto**: Framework de publicación científica
- **Pandas**: Análisis de datos
- **Matplotlib**: Visualización

---

## 📞 Contacto

- **GitHub**: [@estructuraPy](https://github.com/estructuraPy)
- **Proyecto**: [ePy_docs](https://github.com/estructuraPy/ePy_docs)

---

**Versión**: 0.2.0 (Refactorizada)  
**Python**: 3.10+  
**Estado**: En desarrollo activo
