# Citas en Listas y add_content - DIAGNÓSTICO

## Problema Reportado
```python
.add_list([
    "Código Sísmico de Costa Rica (CSCR-2010) [@CSCR2010]",
    "American Concrete Institute ACI 318-19 [@ACI318]",
    "ASCE 7-16 - Minimum Design Loads [@ASCE7]",
    "Reglamento de Construcciones de Costa Rica"
], ordered=True)
```

Las citas no se renderizaban.

## Diagnóstico Realizado

### 1. Verificación del Código ✅
- `add_list()` y `add_content()` **SÍ pasan las citas correctamente** al archivo .qmd
- El archivo .qmd generado muestra las citas en formato correcto: `[@CSCR2010_14]`, `[@ACI318_19]`, etc.
- El mecanismo de copiado de archivos .bib y .csl funciona correctamente

### 2. El Problema Real: Referencias Faltantes ❌
Al revisar `src/ePy_docs/config/assets/bibliography/references.bib`:
- ✅ `CSCR2010_14` - existe
- ✅ `ACI318_19` - existe  
- ❌ `CSCR2010` - NO existe (pero existe `CSCR2010_14`)
- ❌ `ACI318` - NO existe (pero existe `ACI318_19`)
- ❌ `ASCE7` o `ASCE7_16` - NO existe

## Causa Raíz
**Quarto/Pandoc no puede renderizar citas bibliográficas si la clave no existe en el archivo .bib**

Cuando escribes `[@ASCE7]` pero en tu archivo .bib no hay una entrada con `@standard{ASCE7, ...}`, 
Quarto simplemente deja el texto tal cual: "[@ASCE7]" sin procesarlo.

## Solución

### Opción 1: Usar las Claves Correctas (Recomendado)
Usa las claves que **SÍ existen** en tu archivo references.bib:

```python
writer.add_list([
    "Código Sísmico de Costa Rica (CSCR-2010) [@CSCR2010_14]",  # ← clave correcta
    "American Concrete Institute ACI 318-19 [@ACI318_19]",       # ← clave correcta
    "AISC 360-22 - Steel Construction Manual [@AISC360_22]",    # ← esta sí existe
    "Reglamento de Construcciones de Costa Rica"
], ordered=True)
```

### Opción 2: Agregar las Referencias Faltantes
Edita `src/ePy_docs/config/assets/bibliography/references.bib` y agrega:

```bibtex
@standard{ASCE7_16,
  title = {Minimum Design Loads and Associated Criteria for Buildings and Other Structures},
  author = {{American Society of Civil Engineers}},
  organization = {ASCE},
  year = {2016},
  edition = {ASCE/SEI 7-16},
  address = {Reston, VA},
  note = {An American National Standard},
}

@standard{ASCE7_22,
  title = {Minimum Design Loads and Associated Criteria for Buildings and Other Structures},
  author = {{American Society of Civil Engineers}},
  organization = {ASCE},
  year = {2022},
  edition = {ASCE/SEI 7-22},
  address = {Reston, VA},
  note = {An American National Standard},
}
```

## Verificación

El test `test_citas_en_listas.py` demuestra que:
- ✅ Las citas **SÍ funcionan** en `add_text()`
- ✅ Las citas **SÍ funcionan** en `add_content()`
- ✅ Las citas **SÍ funcionan** en `add_list()` (ordenadas y no ordenadas)
- ✅ Sintaxis `[@key]` funciona (parentética)
- ✅ Sintaxis `@key` funciona (narrativa)

**Todas funcionan SOLO si la clave existe en el archivo .bib**

## Referencias que SÍ Existen en references.bib

### Códigos de Costa Rica
- `CSCR2002` - Código Sísmico 2002
- `CSCR2010_14` - Código Sísmico 2010 (edición 2014)
- `CSCR2010_C` - Comentarios al Código Sísmico 2010
- `LDpV2023` - Lineamientos de Diseño por Viento
- `CCCR2009` - Código de Cimentaciones
- `INTEC131_19` - Norma INTECO de prefabricados

### Códigos Internacionales
- `ACI318_19` - ACI 318-19 (Concreto)
- `AISC360_22` - AISC 360-22 (Acero Estructural)
- `AISC341_22` - AISC 341-22 (Diseño Sísmico Acero)
- `AISIS100_16` - Acero Conformado en Frío
- `ASTMA36` - Especificación de Acero Estructural
- `ASTMF1554` - Pernos de Anclaje
- `MSJC2013` - Mampostería

## Ejemplo Completo Funcional

```python
from ePy_docs import DocumentWriter
from pathlib import Path

# Rutas
package_root = Path(__file__).parent / 'src' / 'ePy_docs'
bibliography_file = package_root / 'config' / 'assets' / 'bibliography' / 'references.bib'
csl_file = package_root / 'config' / 'assets' / 'csl' / 'ieee.csl'

# Crear documento
writer = DocumentWriter("paper", layout_style="academic")

writer.add_h2("Normativa Aplicable")

# Método 1: Lista con citas (SOLO usar claves que existen)
writer.add_list([
    "Código Sísmico de Costa Rica (CSCR-2010) [@CSCR2010_14]",
    "American Concrete Institute ACI 318-19 [@ACI318_19]",
    "AISC 360-22 - Steel Construction Manual [@AISC360_22]",
    "Código de Cimentaciones [@CCCR2009]"
], ordered=True)

# Método 2: Texto con múltiples citas
writer.add_content("""
El diseño estructural se realizó conforme a los códigos [@CSCR2010_14; @ACI318_19; @AISC360_22],
considerando las recomendaciones de @LDpV2023 para cargas de viento.
""")

# Método 3: Texto normal
writer.add_text("Según @CSCR2010_14, el factor de zona sísmica debe aplicarse a todas las cargas.")

# Generar
result = writer.generate(
    pdf=True,
    bibliography_path=str(bibliography_file),
    csl_path=str(csl_file)
)
```

## Conclusión

**El código de ePy_docs funciona correctamente.** El problema es simplemente que:
1. Usaste claves (`@ASCE7`, `@CSCR2010`, `@ACI318`) que no existen en tu archivo .bib
2. Necesitas usar las claves exactas: `@ASCE7_16`, `@CSCR2010_14`, `@ACI318_19`
3. O agregar nuevas entradas al archivo references.bib con las claves que prefieras

Las citas **SÍ se renderizan correctamente** en listas, add_content, y add_text cuando 
la clave bibliográfica existe en el archivo .bib.
