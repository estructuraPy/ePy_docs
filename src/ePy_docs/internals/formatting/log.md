# log.md - Módulo _images.py

## Contexto y Funcionamiento

### Propósito
El módulo `_images.py` es parte del "REINO IMAGES" dentro del sistema ePy_docs, encargado de la soberanía absoluta en el manejo de imágenes. Proporciona funcionalidades para procesar, copiar y generar contenido markdown para imágenes en documentos técnicos.

### Arquitectura
- **Configuración centralizada**: Utiliza `get_images_config()` para cargar configuración desde archivos .epyson centralizados.
- **Procesamiento de rutas**: `process_image_path()` normaliza rutas de imágenes para compatibilidad cross-platform y LaTeX.
- **Copia secuencial**: `_copy_image_to_output_directory()` copia imágenes con nomenclatura secuencial (figure_1.png, etc.).
- **Generación de markdown**: Funciones como `add_image_to_content()` y `add_plot_to_content()` crean sintaxis markdown con atributos Quarto.
- **Importación de contenido**: `fix_image_paths_in_imported_content()` procesa imágenes en contenido importado, copiándolas y actualizando referencias.

### Funcionalidades Clave
1. **Adición de imágenes**: Genera markdown con títulos, captions, IDs y atributos responsive.
2. **Manejo de plots**: Similar a imágenes pero con manejo especial para gráficos.
3. **Procesamiento de rutas**: Convierte rutas relativas a absolutas para fiabilidad en LaTeX.
4. **Importación de contenido**: Corrige rutas de imágenes en archivos markdown/quarto importados.

### Integración
- Se integra con el sistema de configuración centralizado (master.epyson).
- Utiliza directorios de salida dinámicos basados en tipo de documento.
- Compatible con Quarto para generación de PDF y HTML.

### Limitaciones y Consideraciones
- Atributo `responsive` comentado para evitar problemas en LaTeX.
- Asume existencia de directorios de configuración.
- Maneja imágenes no encontradas con warnings.

### Potencial de Mejora
- Detección automática de formato de salida para atributos específicos.
- Optimización de copia de imágenes grandes.
- Soporte para más formatos de imagen.

## Historial de Cambios
- **v0.2.0**: Implementación inicial con soberanía del reino IMAGES.
- **Refactorización**: Optimización de código, eliminación de redundancias, mejora de legibilidad.