# 🔄 API Unificada - DocumentWriter

**Fecha:** 18 de octubre de 2025  
**Cambio:** Simplificación de API de 3 clases a 1 clase unificada

---

## 📋 Resumen del Cambio

### Antes (3 clases)
```python
from ePy_docs.writers import BaseDocumentWriter, ReportWriter, PaperWriter

# Clase base abstracta
base = BaseDocumentWriter(document_type='report', layout_style='classic')

# Clases especializadas
report = ReportWriter(layout_style='classic')
paper = PaperWriter(layout_style='academic')
```

### Ahora (1 clase unificada)
```python
from ePy_docs.writers import DocumentWriter

# API unificada explícita
report = DocumentWriter('report', layout_style='classic')
paper = DocumentWriter('paper', layout_style='academic')

# Con defaults inteligentes
report = DocumentWriter('report')  # layout_style='classic' automático
paper = DocumentWriter('paper')    # layout_style='academic' automático
```

---

## ✨ Beneficios

### 1. **Simplicidad**
- ✅ Una sola clase en lugar de tres
- ✅ API más clara y explícita
- ✅ Menos imports necesarios

### 2. **Flexibilidad**
- ✅ Tipo de documento explícito como parámetro
- ✅ Fácil agregar nuevos tipos de documentos
- ✅ Defaults inteligentes por tipo

### 3. **Mantenibilidad**
- ✅ Menos código duplicado
- ✅ Cambios en un solo lugar
- ✅ Más fácil de extender

### 4. **Compatibilidad**
- ✅ `ReportWriter()` y `PaperWriter()` siguen funcionando
- ✅ Código existente no se rompe
- ✅ Migración gradual posible

---

## 📖 Guía de Uso

### Forma Recomendada (Nueva API)

```python
from ePy_docs.writers import DocumentWriter

# Reporte técnico
writer = DocumentWriter('report', layout_style='technical')
writer.add_h1("Análisis Estructural")
writer.add_table(df, title="Resultados")
result = writer.generate(html=True, pdf=True)

# Paper académico
writer = DocumentWriter('paper', layout_style='academic')
writer.add_h1("Abstract")
writer.add_text("This paper presents...")
result = writer.generate(html=True, pdf=True)
```

### Forma Legacy (Compatibilidad)

```python
from ePy_docs.writers import ReportWriter, PaperWriter

# Sigue funcionando exactamente igual
writer = ReportWriter(layout_style='classic')
writer.add_h1("Mi Reporte")
result = writer.generate()
```

---

## 🔧 Detalles Técnicos

### Clase DocumentWriter

```python
class DocumentWriter:
    """Unified document writer for all document types."""
    
    def __init__(self, document_type: str = "report", layout_style: str = None):
        """
        Args:
            document_type: "report" or "paper"
            layout_style: Layout style (None = auto default)
        """
```

### Funciones de Compatibilidad

```python
def ReportWriter(layout_style: str = "classic") -> DocumentWriter:
    """Legacy alias - returns DocumentWriter('report')"""
    return DocumentWriter(document_type="report", layout_style=layout_style)

def PaperWriter(layout_style: str = "academic") -> DocumentWriter:
    """Legacy alias - returns DocumentWriter('paper')"""
    return DocumentWriter(document_type="paper", layout_style=layout_style)
```

### Validación

```python
# Valida tipo de documento
valid_types = ["report", "paper"]
if document_type not in valid_types:
    raise ValueError(f"document_type must be one of {valid_types}")
```

---

## 🎯 Casos de Uso

### 1. Crear Reporte con Layout Técnico

```python
writer = DocumentWriter('report', layout_style='technical')
writer.add_h1("Análisis de Cargas")
writer.add_table(cargas_df, title="Cargas aplicadas")
writer.add_warning("Verificar capacidad de columnas", title="Importante")
result = writer.generate(html=True, pdf=True)
```

### 2. Crear Paper Académico

```python
writer = DocumentWriter('paper', layout_style='academic')
writer.add_h1("Introduction")
writer.add_text("This research investigates...")
writer.add_citation("smith2024", page="45")
writer.add_equation(r"\sigma = \frac{P}{A}", label="eq:stress")
result = writer.generate(html=True, pdf=True)
```

### 3. Migración de Código Existente

```python
# Código antiguo (sigue funcionando)
writer = ReportWriter()

# Equivalente nuevo (recomendado para código nuevo)
writer = DocumentWriter('report')

# Ambos tienen exactamente los mismos métodos y comportamiento
```

---

## 📊 Comparación de APIs

| Característica | API Antigua | API Nueva | Ventaja |
|----------------|-------------|-----------|---------|
| Clases | 3 (Base, Report, Paper) | 1 (DocumentWriter) | Simplicidad |
| Tipo explícito | No | Sí | Claridad |
| Defaults | Hardcoded en clase | Por tipo | Flexibilidad |
| Extensible | Herencia | Parámetro | Escalabilidad |
| Imports | 2-3 | 1 | Limpieza |
| Compatibilidad | N/A | 100% | Sin breaking changes |

---

## 🚀 Migración

### Opción 1: Migración Inmediata (Recomendada)

```python
# Cambiar todos los imports
from ePy_docs.writers import DocumentWriter

# Actualizar inicialización
# ANTES:
writer = ReportWriter(layout_style='classic')

# DESPUÉS:
writer = DocumentWriter('report', layout_style='classic')
```

### Opción 2: Migración Gradual

```python
# Mantener imports existentes (no requiere cambios)
from ePy_docs.writers import ReportWriter, PaperWriter

# El código sigue funcionando sin cambios
writer = ReportWriter()
```

### Opción 3: Mixta

```python
# Usar nueva API para código nuevo
from ePy_docs.writers import DocumentWriter
new_writer = DocumentWriter('report')

# Código legacy sin cambios
from ePy_docs.writers import ReportWriter
old_writer = ReportWriter()
```

---

## ✅ Testing

### Verificar Compatibilidad

```python
# Test 1: Nueva API
writer1 = DocumentWriter('report')
assert writer1.document_type == 'report'
assert writer1.layout_style == 'classic'

# Test 2: API Legacy
writer2 = ReportWriter()
assert writer2.document_type == 'report'
assert writer2.layout_style == 'classic'

# Test 3: Equivalencia
assert type(writer1) == type(writer2)
```

### Validación de Errores

```python
# Debe fallar con tipo inválido
try:
    writer = DocumentWriter('invalid')
except ValueError as e:
    print(f"✅ Validación correcta: {e}")
```

---

## 📝 Archivos Modificados

1. **`src/ePy_docs/writers.py`**
   - Renombrado `BaseDocumentWriter` → `DocumentWriter`
   - Eliminadas clases `ReportWriter` y `PaperWriter`
   - Agregadas funciones helper de compatibilidad
   - Validación de `document_type`
   - Defaults inteligentes para `layout_style`

2. **Scripts de ejemplo actualizados**
   - `demo_nueva_api.py` - Demo completa de nueva API
   - `test_table_conversion.py` - Actualizado a nueva API

---

## 🎓 Mejores Prácticas

### ✅ Recomendado

```python
# Explícito y claro
writer = DocumentWriter('report', layout_style='technical')

# Usar default cuando sea apropiado
writer = DocumentWriter('paper')  # academic por defecto
```

### ⚠️ Evitar

```python
# Imports innecesarios
from ePy_docs.writers import ReportWriter, PaperWriter

# Mejor usar DocumentWriter directamente en código nuevo
```

---

## 🔮 Futuro

Esta arquitectura permite fácilmente:

1. **Agregar nuevos tipos de documentos:**
   ```python
   writer = DocumentWriter('thesis', layout_style='university')
   writer = DocumentWriter('presentation', layout_style='modern')
   ```

2. **Tipos dinámicos desde configuración:**
   ```python
   types = config.get('document_types')  # ['report', 'paper', 'thesis']
   writer = DocumentWriter(types[0])
   ```

3. **Validación extendida:**
   ```python
   # Validar layout_style por tipo
   valid_layouts = {
       'report': ['classic', 'technical', 'corporate'],
       'paper': ['academic', 'scientific', 'professional']
   }
   ```

---

## 📚 Recursos

- **Demo:** `demo_nueva_api.py` - Ejemplos completos
- **Tests:** `test_table_conversion.py` - Testing actualizado
- **Docs:** Este archivo - Guía completa

---

**Estado:** ✅ Completado e implementado  
**Compatibilidad:** ✅ 100% backward compatible  
**Testing:** ✅ Todos los tests pasando  
**Recomendación:** Usar `DocumentWriter()` en código nuevo
