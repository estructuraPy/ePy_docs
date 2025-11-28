# ePy_docs

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-0.1.7-orange)](https://github.com/estructuraPy/ePy_docs)

**Sistema de Generación de Documentación Técnica para Ingeniería**

Librería Python para generar documentación técnica profesional en formatos HTML y PDF, diseñada específicamente para proyectos de ingeniería estructural, geotécnica e hidráulica.

---

## ✨ Características Principales

- 🎯 **API Fluida**: Interfaz intuitiva con method chaining
- 📊 **Tablas Inteligentes**: Detección automática de categorías y colorización
- 📄 **Multi-formato**: Generación simultánea de HTML y PDF vía Quarto
- 🎨 **Layouts Profesionales**: 9 estilos predefinidos (academic, classic, corporate, creative, handwritten, minimal, professional, scientific, technical)
- 🔧 **Integración con ePy_units**: Manejo automático de unidades de ingeniería
- 💬 **Callouts**: Notas, advertencias, tips con estilos predefinidos
- ⚙️ **Configuración Centralizada**: Sistema `.epyson` para configuraciones versionables
- 🚫 **Sin Sincronización**: Lee directamente desde el directorio de instalación

---

## 📦 Instalación

### Instalación Básica

```bash
# Clonar el repositorio
git clone https://github.com/estructuraPy/ePy_docs.git
cd ePy_docs

# Instalar en modo editable
pip install -e .
```

**Durante la instalación, ePy_docs detectará automáticamente las dependencias faltantes y te ofrecerá instalarlas.**

### Configuración Manual de Dependencias

Si prefieres configurar las dependencias después, usa estos comandos:

```bash
# Verificar e instalar todas las dependencias
epy-docs-setup

# O instalar componentes específicos:
epy-docs-install   # Instalar Quarto y TinyTeX
epy-docs-latex     # Instalar paquetes LaTeX (17 paquetes)
```

**Nota:** Los paquetes LaTeX incluyen `fancyvrb` y `framed`, necesarios para el resaltado de código en PDFs.

**Instalación Manual:**

**Windows:**
```powershell
# Instalar Quarto
winget install --id Posit.Quarto

# Instalar TinyTeX
quarto install tinytex
```

**macOS:**
```bash
# Instalar Quarto
brew install quarto

# Instalar TinyTeX
quarto install tinytex
```

**Linux:**
```bash
# Descargar e instalar Quarto desde https://quarto.org/docs/get-started/

# Instalar TinyTeX
quarto install tinytex
```

### Dependencias

**Python (requeridas):**
- Python 3.10+
- pandas >= 2.0.0
- matplotlib >= 3.7.0
- jinja2 >= 3.1.0
- pyyaml >= 6.0
- ePy_units >= 0.1.0

**Externas (para PDF):**
- Quarto >= 1.3.0
- TinyTeX (instalado vía Quarto)

**Nota:** Sin Quarto y TinyTeX, solo podrás generar HTML y DOCX.

---

## 🚀 Uso Básico

### Ejemplo Mínimo

```python
from ePy_docs.writers import ReportWriter
import pandas as pd

# Crear writer
writer = ReportWriter(layout_style='academic')

# Agregar contenido
writer.add_h1("Mi Reporte")
writer.add_text("Este es un reporte técnico.")

# Agregar tabla
df = pd.DataFrame({
    'Elemento': ['C1', 'C2', 'C3'],
    'Fuerza (kN)': [100, 150, 200]
})
writer.add_table(df, title="Resultados")

# Generar outputs
results = writer.generate(html=True, pdf=True)
print(f"HTML: {results['html']}")
print(f"PDF: {results['pdf']}")
```

### Ejemplo con Callouts

```python
# Agregar diferentes tipos de callouts
writer.add_note("Información importante", "Nota")
writer.add_warning("Revisa los valores", "Advertencia")
writer.add_tip("Usa el layout 'corporate' para presentaciones", "Consejo")
writer.add_success("Cálculo verificado correctamente", "Éxito")
```

### Layouts Disponibles

```python
layouts = [
    'academic',      # Estilo académico clásico
    'classic',       # Estilo clásico
    'corporate',     # Presentaciones corporativas
    'creative',      # Diseño creativo
    'handwritten',   # Estilo manuscrito
    'minimal',       # Diseño minimalista
    'professional',  # Estilo profesional
    'scientific',    # Diseño científico
    'technical'      # Documentación técnica
]

writer = ReportWriter(layout_style='corporate')
```

---

## 🎨 Sistema de Configuración

### Archivos .epyson

Los archivos de configuración usan la extensión `.epyson` (ePy Source Object Notation):

```
.epyson  → Configuración fuente (versionado en git)
.epyx    → Cache intermedio (temporal, no versionado)
.json    → Salida procesada (generado, no versionado)
```

### Ejemplo de Configuración

```json
{
  "palettes": {
    "default": {
      "primary": "#2E86AB",
      "secondary": "#A23B72",
      "success": "#06A77D",
      "warning": "#F18F01",
      "danger": "#C73E1D"
    }
  }
}
```

---

## 📁 Estructura del Proyecto

```
ePy_docs/
├── 📂 src/ePy_docs/                  # Código fuente
│   ├── __init__.py
│   ├── writers.py                    # ReportWriter, PaperWriter
│   ├── config/                       # Sistema de configuración
│   │   ├── translations.epyson
│   │   ├── assets/
│   │   │   ├── colors.epyson
│   │   │   ├── fonts/
│   │   │   └── bibliography/
│   │   ├── documents/
│   │   │   ├── book.epyson
│   │   │   ├── notebook.epyson
│   │   │   ├── paper.epyson
│   │   │   └── report.epyson
│   │   └── layouts/
│   │       ├── academic.epyson
│   │       ├── classic.epyson
│   │       ├── corporate.epyson
│   │       ├── creative.epyson
│   │       ├── handwritten.epyson
│   │       ├── minimal.epyson
│   │       ├── professional.epyson
│   │       ├── scientific.epyson
│   │       └── technical.epyson
│   └── core/                         # Módulos internos
│       ├── _quarto.py                # Integración Quarto
│       ├── _config.py                # Configuración
│       ├── _tables.py                # Procesamiento de tablas
│       ├── _text.py                  # Procesamiento de texto
│       ├── _notes.py                 # Callouts
│       ├── _images.py                # Imágenes
│       ├── _colors.py                # Paletas
│       └── ...
├── 📂 data/                          # Datos de ejemplo
│   ├── robot/                        # Datos de Robot Structural
│   └── user/                         # Proyectos de usuario
├── pyproject.toml                    # Configuración del proyecto
├── LICENSE
└── README.md
```

---

## 🔧 API Reference

### ReportWriter

**Clase principal para generar reportes técnicos.**

```python
ReportWriter(
    layout_style: str = 'classic',
    document_type: str = 'report',
    language: str = 'es'
)
```

**Métodos:**

- `add_h1(text)`, `add_h2(text)`, `add_h3(text)`: Agregar encabezados
- `add_text(content)`: Agregar texto
- `add_list(items, ordered=False)`: Agregar listas
- `add_table(df, title, **kwargs)`: Agregar tabla con formato inteligente
- `add_colored_table(df, title, color_column, **kwargs)`: Agregar tabla con mapa de calor
- `add_note(content, title)`: Agregar nota
- `add_tip(content, title)`: Agregar consejo
- `add_warning(content, title)`: Agregar advertencia
- `add_success(content, title)`: Agregar éxito
- `generate(html=True, pdf=False)`: Generar documentos

---

## 🧪 Testing

Los tests están integrados en notebooks de Jupyter:

```bash
# Abrir notebook de test
jupyter notebook test_01_basic_report.ipynb

# O ejecutar demo completo
jupyter notebook demo_unified_api.ipynb
```

---

## 📚 Documentación

- **[Análisis de Calidad](docs/CODE_QUALITY_ANALYSIS.md)**: Revisión SOLID y mejores prácticas
- **[Nueva Estructura](docs/NUEVA_ESTRUCTURA.md)**: Detalles de la reorganización
- **[Session Summary](docs/SESSION_SUMMARY.md)**: Resumen de sesiones de desarrollo

---

## 🛠️ Desarrollo

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

Este proyecto es privado.

---

## 👥 Autores

- **estructuraPy** - Desarrollo inicial

---

## 🙏 Agradecimientos

- **ePy_units**: Sistema de unidades de ingeniería
- **Quarto**: Framework de publicación científica
- **Pandas**: Análisis de datos
- **Matplotlib**: Visualización
- **Citation Style Language**: Para estilos de citación - [Ver repositorio](https://github.com/citation-style-language/styles)

---

## 📞 Contacto

- **GitHub**: [@estructuraPy](https://github.com/estructuraPy)
- **Proyecto**: [ePy_docs](https://github.com/estructuraPy/ePy_docs)

---

**Versión**: 0.1.7  
**Python**: 3.10+  
**Estado**: En desarrollo activo
