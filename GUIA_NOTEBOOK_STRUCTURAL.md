# 📘 Guía: report_structural_CLEAN.ipynb

## 🎯 Propósito

Este notebook demuestra el **flujo completo** de generación de un reporte estructural profesional usando ePy_docs.

## ✅ Características

- **UN SOLO PDF** generado al final
- Flujo lineal sin duplicaciones
- Datos reales de análisis estructural (nodos, reacciones, elementos)
- Gráficos matplotlib integrados
- Tablas coloreadas con paleta engineering
- Ecuaciones LaTeX
- Callouts (note, tip, warning, important, success)
- Referencias bibliográficas con ACI318 y CSCR2010

## 📊 Estructura del Notebook

### Sección 1: Configuración Inicial
- **Celdas 1-3**: Markdown (introducción)
- **Celda 4**: Imports y configuración de rutas
- **Celda 5**: Verificación de archivos de datos

### Sección 2: Inicialización del Writer
- **Celda 6**: Creación del `ReportWriter` con layout `classic`
- **Celda 7**: Configuración de información del proyecto

### Sección 3: Carga de Datos
- **Celdas 8-10**: 
  - Carga de `nodes.csv`
  - Carga de `reactions.csv`
  - Preparación de DataFrames

### Sección 4: Contenido del Reporte
- **Celda 11**: Demostración gráfica completa
  - Gráfico de barras de reacciones
  - Tabla coloreada de reacciones
  - Ecuaciones teóricas
  - Diagrama del modelo estructural

- **Celda 12**: Agregación de secciones adicionales
  - Tablas simples
  - Imágenes externas

### Sección 5: Contenido Avanzado
- **Celdas 13-45**: Demostración de funcionalidades
  - Chunks de código
  - Callouts de todos los tipos
  - Ecuaciones matemáticas
  - Tablas con diferentes formatos
  - Referencias bibliográficas

### Sección 6: Generación Final
- **Celda 46**: Markdown de inclusión de archivo externo
- **Celda 47**: Imagen de logo
- **Celda 48**: **GENERACIÓN ÚNICA DE PDF/HTML**
  ```python
  writer.generate(pdf=True, html=True, citation_style='apa')
  ```

## 🚀 Cómo Usar

### Ejecución Completa
1. Abrir `report_structural_CLEAN.ipynb`
2. **Run All Cells** (Ctrl+Shift+Enter)
3. Esperar a que termine la celda 48
4. Verificar PDF generado en `results/report/`

### Ejecución Paso a Paso
1. Ejecutar celdas 1-10 (setup y carga de datos)
2. Revisar DataFrames cargados
3. Ejecutar celdas 11-47 (agregación de contenido)
4. **Ejecutar celda 48 UNA SOLA VEZ**
5. Verificar output en `results/report/`

## ⚠️ Importante

### ❌ NO HACER
- NO ejecutar la celda 48 más de una vez
- NO crear celdas adicionales de generación
- NO modificar rutas de archivos sin verificar que existan

### ✅ SÍ HACER
- Ejecutar todo el notebook de principio a fin
- Verificar que los archivos CSV existan antes de ejecutar
- Revisar outputs de matplotlib antes de generar PDF
- Usar `writer.generate(pdf=True, html=True)` en UNA SOLA celda

## 📁 Archivos Requeridos

```
data/robot/
  ├── nodes.csv           # Coordenadas de nodos
  ├── reactions.csv       # Fuerzas de reacción
  ├── elements.csv        # Elementos estructurales
  └── combinations.csv    # Combinaciones de carga

data/user/brand/
  └── logo.png           # Logo de la empresa

results/report/         # Output generado
  ├── STRUCT-2025-001.pdf
  ├── STRUCT-2025-001.html
  ├── reactions_plot.png
  └── structural_model.png
```

## 🔍 Verificación de Salida

### PDF Exitoso
```
✅ Archivo: STRUCT-2025-001.pdf
✅ Tamaño: ~30-40 KB
✅ Contenido:
   - Portada con información del proyecto
   - 7 secciones principales
   - 10+ tablas
   - 5+ figuras
   - Ecuaciones LaTeX
   - Referencias bibliográficas
   - Formato de 1 columna
```

### HTML Exitoso
```
✅ Archivo: STRUCT-2025-001.html
✅ Formato: Responsivo
✅ Contenido: Idéntico al PDF
✅ Imágenes: Embebidas o referenciadas
```

## 🐛 Troubleshooting

### Error: "File not found"
**Causa**: Archivos CSV no existen
**Solución**: Verificar rutas en `data/robot/`

### Error: "No module named 'ePy_docs'"
**Causa**: Paquete no instalado
**Solución**: 
```powershell
pip install -e .
```

### Error: "Quarto not found"
**Causa**: Quarto no instalado
**Solución**: Instalar Quarto 1.4+

### Warning: "Multiple PDF generations"
**Causa**: Celda 48 ejecutada múltiples veces
**Solución**: 
1. Restart kernel
2. Run All Cells una sola vez

## 📚 Diferencias con Otros Notebooks

### vs `demo_simple_pdf.ipynb`
- ✅ `report_structural_CLEAN`: Datos reales, contenido completo
- ⚠️ `demo_simple_pdf`: Ejemplo mínimo, datos ficticios

### vs `report_structural_example.ipynb`
- ✅ `report_structural_CLEAN`: Limpio, sin errores, ejecución garantizada
- ❌ `report_structural_example`: Tenía errores en celda 14, estado inconsistente

### vs `demo_complete_api.ipynb`
- 🔬 `demo_complete_api`: Demostración exhaustiva de API (68 ejecuciones)
- 🏗️ `report_structural_CLEAN`: Caso práctico de ingeniería estructural

## 🎓 Aprendizaje

Este notebook enseña:
1. **Flujo lineal**: Setup → Datos → Contenido → Generación
2. **Method chaining**: Encadenamiento de métodos del writer
3. **Integración matplotlib**: Gráficos embebidos en PDF
4. **Tablas profesionales**: Formato engineering con colores
5. **Ecuaciones técnicas**: LaTeX con numeración automática
6. **Referencias**: Sistema de citación académica

## 🔗 Referencias

- **ePy_docs API**: `src/ePy_docs/writers.py`
- **Layouts disponibles**: `src/ePy_docs/internals/generation/pages.epyson`
- **Paletas de color**: `src/ePy_docs/internals/styling/_colors.py`
- **Guía simple**: `GUIA_PDF_SIMPLE.md`

---

**Versión**: 1.0
**Fecha**: 2025
**Autor**: ePy_docs Team
**Estado**: ✅ FUNCIONAL - LISTO PARA PRODUCCIÓN
