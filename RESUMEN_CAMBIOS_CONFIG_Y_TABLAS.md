# Resumen de Cambios: Configuración y Conversión de Tablas Markdown

## Fecha: 2025-10-18

### 1. Corrección del ConfigManager

**Problema identificado:**
- El `ConfigManager` usaba rutas absolutas hardcodeadas que solo funcionaban en modo desarrollo
- Las rutas de los archivos `.epyson` estaban duplicadas en el código

**Solución implementada:**

#### Parte 1: Rutas relativas al paquete
Archivo: `src/ePy_docs/config/config_manager.py`

```python
# ANTES (incorrecto):
self.base_path = Path(__file__).parent.parent.parent.parent
self.config_path = self.base_path / "src" / "ePy_docs" / "config"

# DESPUÉS (correcto):
self.package_path = Path(__file__).parent.parent  # Directorio del paquete instalado
self.config_path = Path(__file__).parent          # config/
```

#### Parte 2: Configuración centralizada en setup.epyson
Archivo: `src/ePy_docs/config/setup.epyson`

Se agregó la sección `config_files` que define las rutas relativas de todos los archivos de configuración:

```json
{
  "config_files": {
    "colors": "internals/styling/colors.epyson",
    "tables": "internals/formatting/tables.epyson",
    "text": "internals/formatting/text.epyson",
    "images": "internals/formatting/images.epyson",
    "pages": "internals/generation/pages.epyson",
    "report": "report.epyson",
    "paper": "internals/generation/paper.epyson",
    "format": "internals/formatting/format.epyson",
    "code": "internals/formatting/code.epyson",
    "mapper": "internals/formatting/mapper.epyson",
    "project_info": "project_info.epyson",
    "notes": "internals/formatting/notes.epyson",
    "html": "internals/generation/html.epyson",
    "pdf": "internals/generation/pdf.epyson",
    "references": "internals/generation/references.epyson"
  }
}
```

#### Parte 3: ConfigManager lee rutas desde setup.epyson

```python
def _load_all_configs(self):
    # 1. Cargar setup.epyson primero
    setup_config = json.load(open(setup_path))
    self._configs['setup'] = setup_config
    
    # 2. Obtener rutas de archivos desde setup
    config_files = setup_config.get('config_files', {})
    
    # 3. Cargar cada archivo usando las rutas del setup
    for config_name, relative_path in config_files.items():
        config_path = self.package_path / relative_path
        self._configs[config_name] = json.load(open(config_path))
```

**Beneficios:**
- ✅ Sin hardcodeo de rutas en el código Python
- ✅ Todas las rutas definidas en un solo archivo de configuración
- ✅ Fácil modificar ubicaciones sin tocar código
- ✅ Funciona en instalaciones del paquete y en desarrollo

---

### 2. Conversión Automática de Tablas Markdown

**Nueva funcionalidad:**
Al importar archivos `.md` o `.qmd`, las tablas en formato Markdown se detectan automáticamente, se convierten en DataFrames de pandas, y se agregan usando `add_table()` para aplicar el estilo configurado.

**Archivos creados:**

#### `src/ePy_docs/utils/markdown_parser.py`
Nuevas funciones para parsear tablas Markdown:

- `extract_markdown_tables(content)`: Extrae todas las tablas y sus captions
- `_parse_markdown_table(table_lines)`: Convierte líneas Markdown a DataFrame
- `remove_tables_from_content(content, tables_info)`: Remueve tablas e inserta placeholders

**Características:**
- Detecta tablas con formato estándar Markdown (`| Header | ... |`)
- Reconoce captions antes de la tabla (`:  Caption` o `Tabla X: Caption`)
- Convierte automáticamente columnas numéricas
- Preserva el orden original del contenido

#### Modificaciones en `src/ePy_docs/writers.py`

**Método `add_markdown_file()` actualizado:**

```python
def add_markdown_file(self, file_path: str, fix_image_paths: bool = True, 
                     convert_tables: bool = True) -> 'BaseDocumentWriter':
    """
    Args:
        file_path: Path to the .md file to include
        fix_image_paths: Whether to fix image paths (default: True)
        convert_tables: Whether to convert Markdown tables to styled tables (default: True)
    """
```

**Método `add_quarto_file()` actualizado:**

```python
def add_quarto_file(self, file_path: str, include_yaml: bool = False, 
                   fix_image_paths: bool = True, convert_tables: bool = True) -> 'BaseDocumentWriter':
    """
    Args:
        file_path: Path to the .qmd file to include
        include_yaml: Whether to include YAML frontmatter (default: False)
        fix_image_paths: Whether to fix image paths (default: True)
        convert_tables: Whether to convert Markdown tables to styled tables (default: True)
    """
```

**Proceso de conversión:**

1. **Lectura**: Lee el archivo original
2. **Extracción**: Identifica todas las tablas Markdown
3. **Remoción**: Reemplaza tablas con placeholders
4. **Procesamiento**: Procesa el contenido sin tablas
5. **Intercalado**: Inserta tablas estilizadas usando `add_table()` en posiciones originales

**Ejemplo de entrada (Markdown):**

```markdown
## Resultados

: Análisis estructural

| Elemento | Fuerza (kN) | Estado |
|----------|-------------|---------|
| Viga-01  | 125.5       | OK      |
| Columna-01 | 450.2     | OK      |
```

**Salida (procesada por ePy_docs):**

- El texto se preserva
- La tabla se convierte en DataFrame de pandas
- Se aplica estilo según `layout_style` configurado
- Se genera imagen PNG con la tabla estilizada
- Se inserta en la posición original con sintaxis Quarto

---

### 3. Testing

**Archivo de prueba:** `test_markdown_tables.md`

Contiene:
- 2 tablas Markdown con diferentes datos
- Captions con diferentes formatos
- Texto intermedio para verificar orden

**Script de prueba:** `test_table_conversion.py`

Verifica:
- ✅ Extracción correcta de tablas
- ✅ Preservación del orden del contenido
- ✅ Generación de imágenes de tablas
- ✅ Captions correctamente asignados

**Resultado de la prueba:**
```
✅ Documento generado
✅ 16 configuraciones cargadas (setup + 15 archivos .epyson)
📊 2 tablas convertidas correctamente (table_49.png, table_50.png)
✅ Orden del contenido preservado
✅ Sin errores ni warnings
```

---

### 4. Beneficios

1. **Portabilidad mejorada**: ConfigManager funciona en cualquier instalación
2. **Automatización**: No es necesario convertir manualmente tablas Markdown
3. **Consistencia**: Todas las tablas usan el mismo estilo configurado
4. **Flexibilidad**: Opción `convert_tables=False` para deshabilitar conversión
5. **Preservación**: Orden y estructura del documento original se mantienen

---

### 5. Uso

#### Conversión activada (por defecto):

```python
from ePy_docs.writers import ReportWriter

writer = ReportWriter(layout_style="technical")
writer.add_markdown_file("documento.md")  # Tablas se convierten automáticamente
writer.generate(html=True, pdf=True)
```

#### Conversión desactivada:

```python
writer.add_markdown_file("documento.md", convert_tables=False)  # Tablas permanecen en Markdown
```

#### Con archivos Quarto:

```python
writer.add_quarto_file("analisis.qmd", convert_tables=True)  # También funciona con .qmd
```

---

### 6. Archivos modificados

**Configuración:**
- ✅ `src/ePy_docs/config/config_manager.py` - Lectura de rutas desde setup.epyson
- ✅ `src/ePy_docs/config/setup.epyson` - Agregada sección `config_files`
- ✅ `src/ePy_docs/internals/generation/pdf.epyson` - Creado con configuración básica

**Conversión de tablas:**
- ✅ `src/ePy_docs/writers.py` - Conversión de tablas agregada a add_markdown_file() y add_quarto_file()
- ✅ `src/ePy_docs/utils/markdown_parser.py` - Nueva utilidad (creada)

### 7. Archivos de prueba creados

- ✅ `test_markdown_tables.md` - Documento de prueba
- ✅ `test_table_conversion.py` - Script de validación

---

## Próximos pasos sugeridos

1. Agregar soporte para tablas con colspan/rowspan
2. Mejorar detección de tipos de datos numéricos
3. Agregar tests unitarios para `markdown_parser.py`
4. Documentar en README.md el uso de `convert_tables`

---

**Estado:** ✅ Completado y verificado
**Autor:** GitHub Copilot
**Fecha:** 18 de octubre de 2025
