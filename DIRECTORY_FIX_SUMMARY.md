# Corrección del problema de configuración de directorios

## Problema identificado

El problema principal era que los directorios definidos en `setup.json` no se estaban respetando correctamente en algunos casos, resultando en:

1. Carpetas vacías creadas en ubicaciones incorrectas
2. El reporte quedando en una ubicación incorrecta
3. Inconsistencias entre rutas relativas y absolutas

## Causa raíz

La función `get_output_directories()` devuelve paths relativos desde `setup.json`, pero en varios lugares del código se estaban usando estos paths relativos como si fueran absolutos, o se estaban combinando incorrectamente con `self.output_dir` sin tener en cuenta el directorio base correcto.

## Solución implementada

### 1. Nueva función utilitaria en `setup.py`

Se agregó la función `get_absolute_output_directories()` que:
- Convierte automáticamente todos los paths relativos de `setup.json` a paths absolutos
- Usa el directorio de trabajo actual como base por defecto
- Permite especificar un directorio base personalizado

```python
def get_absolute_output_directories(sync_json: bool = False, base_dir: str = None) -> Dict[str, str]:
    """Get all directories from setup.json configuration as absolute paths."""
```

### 2. Correcciones en archivos principales

#### `src/ePy_docs/api/report.py`
- Cambiado de `get_output_directories()` a `get_absolute_output_directories()`
- Eliminada lógica redundante de conversión a path absoluto
- Garantiza que `self.output_dir` siempre sea un path absoluto correcto

#### `src/ePy_docs/core/markdown.py`
- Todas las instancias de `get_output_directories()` cambiadas a `get_absolute_output_directories()`
- Eliminada lógica de `os.path.basename()` y `os.path.join(self.output_dir, subdir)`
- Simplificado el código usando paths absolutos directamente

#### `src/ePy_docs/core/quarto.py`
- Actualizada la lógica de creación de directorios para reportes QMD
- Usa paths absolutos directamente desde la configuración

#### `src/ePy_docs/components/images.py`
- Actualizado para usar paths absolutos para las figuras
- Eliminada lógica de construcción manual de paths

#### `src/ePy_docs/units/converter.py`
- Todas las funciones que usan configuración de directorios actualizadas
- Garantiza paths absolutos para archivos de configuración de unidades

### 3. Cambios específicos

| Archivo | Líneas afectadas | Cambio principal |
|---------|-----------------|------------------|
| `setup.py` | 100-125 | Nueva función `get_absolute_output_directories()` |
| `api/report.py` | 33, 42-48 | Uso de paths absolutos en inicialización |
| `core/markdown.py` | 169-174, 297-301, 409-414, 503-507, 743-747, 760-764 | Todas las instancias de creación de directorios |
| `core/quarto.py` | 617-625 | Creación de directorio de reportes |
| `components/images.py` | 249-254, 319-324 | Creación de directorio de figuras |
| `units/converter.py` | 9, 735, 824, 834 | Configuración de directorios de unidades |

## Verificación

Se creó y ejecutó un script de prueba que confirmó:

1. ✅ La configuración relativa se lee correctamente desde `setup.json`
2. ✅ Los paths absolutos se construyen correctamente
3. ✅ Los directorios se crean en las ubicaciones correctas
4. ✅ `ReportWriter` se inicializa con el directorio correcto
5. ✅ No se crean más carpetas vacías en ubicaciones incorrectas

## Estructura de directorios resultante

Ahora todos los componentes respetan la configuración de `setup.json`:

```
results/
├── figures/          # Figuras globales (si las hay)
├── tables/           # Tablas globales (si las hay)
└── report/           # Directorio principal de reportes
    ├── figures/      # Figuras del reporte
    ├── tables/       # Tablas del reporte
    └── [archivos.md] # Archivos markdown del reporte
```

## Impacto

- ✅ No más carpetas vacías en ubicaciones incorrectas
- ✅ Los reportes se generan en `results/report/` según `setup.json`
- ✅ Las imágenes y tablas se organizan correctamente
- ✅ Consistencia en todo el código base
- ✅ Mayor confiabilidad en la gestión de paths
- ✅ Código más limpio y mantenible
