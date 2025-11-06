# Multi-Column Table Parsing Fix

## Problem

Algunas tablas en archivos markdown/quarto no se estaban detectando y parseando correctamente. Específicamente, tablas con **headers multi-nivel** donde las filas de datos tienen más columnas que el header.

### Ejemplos de tablas problemáticas:

**Tabla 1: Condición de análisis**
```markdown
| Condición de análisis | Riesgo de daños... | Riesgo de pérdida... |
| :------ | :------ | :------ |
|         |         | Bajo | Medio | Alto |    <- 5 columnas (header tiene 3)
| Estática| Bajo    | 1,20 | 1,30  | 1,40 |
```

**Tabla 2: Tipo de sitio**
```markdown
| Tipo de sitio | Coeficientes 150 años | Coeficientes 475 años |
| :------ | :------ | :------ |
|         | Zona II | Zona III | Zona IV | Zona II | Zona III | Zona IV |    <- 7 columnas
```

### Causa raíz

El parser asumía que todas las filas tenían el mismo número de columnas que el header. Cuando una fila tenía más columnas, `pandas.DataFrame(data, columns=header)` fallaba con error de dimensiones incompatibles.

## Solution

Mejoré el parser para manejar tablas con número variable de columnas:

### Cambios en código

**Archivos modificados:**
- `src/ePy_docs/core/_markdown.py` (lines 325-360)
- `src/ePy_docs/core/_quarto.py` (lines 560-590)

**Lógica nueva:**

1. **Detectar número máximo de columnas** en toda la tabla:
```python
max_cols = max(len(row) for row in parsed_rows)
```

2. **Rellenar filas con menos columnas** con strings vacíos:
```python
for row in parsed_rows:
    while len(row) < max_cols:
        row.append('')
```

3. **Generar nombres de columna adicionales** si el header tiene menos columnas que los datos:
```python
header = parsed_rows[0]
if len(header) < max_cols:
    for i in range(len(header), max_cols):
        header.append(f'Unnamed_{i}')
```

4. **Crear DataFrame** con todas las filas del mismo ancho:
```python
df = pd.DataFrame(parsed_rows[1:], columns=header)
```

### Comportamiento

**Antes:**
- Tablas con columnas variables: ❌ Error o ignoradas
- Parsing fallaba silenciosamente
- Las tablas aparecían como texto plano en el documento

**Después:**
- Tablas con columnas variables: ✅ Parseadas correctamente
- Columnas extra nombradas como `Unnamed_3`, `Unnamed_4`, etc.
- Todas las filas se rellenan al mismo ancho
- Tablas se convierten a imágenes styled correctamente

## Testing

### Test 1: Tablas sintéticas
**Archivo:** `test_multicolumn_tables.py`

```python
# Tabla con 3 cols header → 5 cols data
| Condición | Riesgo económico | Riesgo vidas |
|-----------|------------------|--------------|
|           |                  | Bajo | Medio | Alto |
| Estática  | Bajo             | 1,20 | 1,30  | 1,40 |

# Tabla con 3 cols header → 7 cols data
| Tipo | Coef 150 años | Coef 475 años |
|------|---------------|---------------|
|      | Z-II | Z-III | Z-IV | Z-II | Z-III | Z-IV |
| S1   | 0,10 | 0,10  | 0,15 | 0,15 | 0,15  | 0,20 |
```

**Resultado:** ✅ Ambas tablas parseadas sin errores

### Test 2: Archivo real
**Archivo:** `test_rockfill_tables.py`

Procesa `data/user/document/03_geotech/rockfill.qmd` que contiene las dos tablas problemáticas reportadas por el usuario.

**Resultado:**
```
✓ File parsed successfully without errors
✓ Content added to document (13037 characters)
✓ Table 1 (Condición de análisis) was processed
✓ Table 2 (Tipo de sitio) was processed
```

## Impact

✅ **Tablas multi-nivel:** Ahora se detectan y parsean correctamente
✅ **Columnas variables:** Headers con menos columnas que datos funcionan
✅ **Compatibilidad:** Tablas normales siguen funcionando igual
✅ **Robustez:** Todas las filas se normalizan al mismo ancho
✅ **Nombres automáticos:** Columnas extra se nombran `Unnamed_N`

## Files Modified

```
src/ePy_docs/core/_markdown.py    (lines 325-360)
src/ePy_docs/core/_quarto.py      (lines 560-590)
```

## Tests Created

```
test_multicolumn_tables.py        (synthetic tables test)
test_rockfill_tables.py           (real file validation)
```

## Validation

Ejecutar tests:
```bash
python test_multicolumn_tables.py    # Tablas sintéticas
python test_rockfill_tables.py       # Archivo real del usuario
```

Ambos tests pasan exitosamente ✅
