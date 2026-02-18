# Guía de Revisión de Código Efectiva

## Introducción

La revisión de código es una práctica fundamental en el desarrollo profesional de software que implica el análisis sistemático del código fuente por parte de desarrolladores que no son los autores originales. Este proceso mejora la calidad del código, facilita la transferencia de conocimiento y reduce los defectos antes de que lleguen a producción.

## Objetivos de la Revisión de Código

- **Mejorar la calidad**: Identificar errores, vulnerabilidades y problemas de diseño.
- **Compartir conocimiento**: Facilitar el aprendizaje entre miembros del equipo.
- **Asegurar consistencia**: Mantener un estilo y arquitectura coherentes.
- **Verificar requisitos**: Comprobar que el código implementa las funcionalidades requeridas.
- **Reducir deuda técnica**: Identificar y corregir prácticas que podrían generar problemas a futuro.

## Proceso de Revisión de Código

### Preparación

1. **Establecer estándares claros**: Definir guías de estilo, patrones de diseño y prácticas recomendadas.
2. **Crear listas de verificación**: Desarrollar checklists específicas según los requerimientos del proyecto.
3. **Automatizar lo posible**: Usar herramientas de análisis estático como flake8, pylint o black.

### Durante la Revisión

1. **Limitar el tamaño**: Revisar cambios pequeños e incrementales (idealmente menos de 400 líneas).
2. **Establecer un tiempo límite**: Sesiones de no más de 60-90 minutos para mantener la efectividad.
3. **Adoptar una mentalidad constructiva**: Enfocarse en mejorar el código, no en criticar al desarrollador.
4. **Priorizar aspectos**: Centrarse primero en problemas de diseño y lógica, luego en estilo y formato.

### Después de la Revisión

1. **Dar seguimiento**: Verificar que los problemas identificados se resuelvan.
2. **Iterar**: Realizar múltiples revisiones si es necesario.
3. **Reflexionar y mejorar**: Evaluar periódicamente el proceso de revisión y ajustarlo.

## Aspectos a Evaluar

### Funcionalidad

- ¿El código cumple con los requisitos especificados?
- ¿Maneja correctamente los casos borde y situaciones excepcionales?
- ¿Las pruebas cubren adecuadamente la funcionalidad?

### Legibilidad y Mantenibilidad

- ¿El código es fácil de entender?
- ¿Los nombres de variables, funciones y clases son descriptivos?
- ¿Hay documentación adecuada (docstrings, comentarios)?
- ¿Se siguen las convenciones de estilo establecidas (PEP 8)?

```python
# Ejemplo de código con buena legibilidad
def calculate_average_score(student_scores):
    """
    Calculate the average score from a list of student scores.
    
    Args:
        student_scores: List of numerical scores
        
    Returns:
        float: The average score or 0 if list is empty
    """
    if not student_scores:
        return 0
        
    return sum(student_scores) / len(student_scores)
```

### Arquitectura y Diseño

- ¿El código sigue principios SOLID?
- ¿La estructura facilita la reutilización y extensión?
- ¿Hay una separación adecuada de responsabilidades?
- ¿Se utilizan patrones de diseño apropiados?

### Rendimiento

- ¿El código es eficiente en términos de tiempo y memoria?
- ¿Se utilizan estructuras de datos apropiadas?
- ¿Hay operaciones que podrían optimizarse?

```python
# Ejemplo de optimización
# Menos eficiente
result = []
for i in range(1000):
    if i % 2 == 0:
        result.append(i * i)

# Más eficiente (comprensión de lista)
result = [i * i for i in range(1000) if i % 2 == 0]
```

### Seguridad

- ¿Se validan adecuadamente las entradas?
- ¿Se manejan correctamente los datos sensibles?
- ¿El código es vulnerable a ataques comunes (inyección, XSS, etc.)?
- ¿Se utilizan métodos seguros para operaciones críticas?

### Manejo de Errores

- ¿Se gestionan adecuadamente las excepciones?
- ¿Los mensajes de error son útiles y descriptivos?
- ¿Se registran (log) los errores importantes?

```python
# Buen manejo de errores
try:
    with open(filename, 'r') as file:
        data = json.load(file)
except FileNotFoundError:
    logger.error(f"El archivo {filename} no fue encontrado")
    raise
except json.JSONDecodeError as e:
    logger.error(f"Error al decodificar JSON: {e}")
    raise ValueError(f"El archivo {filename} no contiene JSON válido") from e
```

## Proporcionar Feedback Efectivo

### Principios para el Feedback

1. **Ser específico**: Indicar exactamente qué y dónde está el problema.
2. **Ser objetivo**: Basarse en hechos y estándares, no en preferencias personales.
3. **Ser constructivo**: Ofrecer soluciones o alternativas, no sólo señalar problemas.
4. **Ser respetuoso**: Mantener un tono profesional y cordial.

### Ejemplos de Feedback

#### Inefectivo
- "Este código es confuso."
- "¿Por qué no usaste X?"
- "Esto está mal."

#### Efectivo
- "La función `process_data()` podría ser más clara si se dividiera en subfunciones para cada etapa del procesamiento."
- "Considero que usar un diccionario en lugar de múltiples if-elif podría hacer este código más mantenible porque [razón]."
- "Esta implementación podría tener un problema con valores nulos. ¿Has considerado añadir una validación aquí?"

## Herramientas para Revisiones de Código en Python

### Análisis Estático

- **Flake8**: Combina PyFlakes, pycodestyle y circular complexity checker.
- **Pylint**: Análisis más exhaustivo con verificaciones adicionales.
- **Mypy**: Verificación de tipos estáticos.
- **Black**: Formateador de código automático.
- **isort**: Organizador de importaciones.

### Integración con Control de Versiones

- **GitHub Pull Requests**: Sistema integrado de revisión de código.
- **GitLab Merge Requests**: Similar a GitHub, con capacidades CI/CD integradas.
- **Gerrit**: Sistema especializado en revisión de código para Git.

### CI/CD para Revisiones

- **Pre-commit hooks**: Verificaciones automáticas antes de confirmar cambios.
- **GitHub Actions/GitLab CI**: Ejecución automática de análisis y pruebas.

## Ejemplo de Flujo de Trabajo de Revisión

1. **Desarrollador**:
   - Implementa la función requerida
   - Ejecuta herramientas de análisis estático
   - Escribe pruebas unitarias
   - Solicita revisión (Pull Request)

2. **Revisor**:
   - Verifica que el código pase CI/CD
   - Revisa el diseño y la arquitectura
   - Examina la funcionalidad y legibilidad
   - Proporciona comentarios específicos

3. **Desarrollador**:
   - Responde a los comentarios
   - Realiza cambios necesarios
   - Solicita re-revisión si es necesario

4. **Revisor**:
   - Verifica los cambios
   - Aprueba o solicita más cambios


# Listas de Verificación para Revisores de Código

## Etapa 1: Código python

En esta etapa se pretende una revisión rápida para confirmar el cumplimiento de los criterios:. converter.py es intocable. 

### Diseño
- [ ] ¿Sigue el código los principios SOLID?
- [ ] ¿Las clases y funciones tienen una única responsabilidad?
- [ ] ¿Las clases y funciones tienen una única responsabilidad?
- [ ] Usa Liskov Substitution
- [ ] Sin rastros de backward compability[ ] ¿El código evita la duplicación?
- [ ] ¿Las abstracciones son adecuadas?
- [ ] Módulos de máximo 1000 líneas. Inaceptable más de 1100. 
- [ ] La separación de módulos es temática.
- [ ] El código no tiene hardcodeado, respeta la convención epyx, epyson y json y les da prioridad.
- [ ] Objetivo es minimizar líneas de código y módulos, optimizando procesos y sin redundancia.

### Funcionalidad
- [ ] ¿El código implementa todos los requisitos?
- [ ] ¿Las pruebas cubren casos normales y excepcionales?
- [ ] ¿El código maneja correctamente los casos borde?
- [ ] No hay prints excesivos y DEBUGS.
- [ ] Usa como referencia el log.md para comprender el contexto global de la librería y de esta forma mejorar la optimización inter-módulo, pero centrada en el módulo que se está mejorando.  Al final, actualiza log.md.

### Legibilidad
- [ ] ¿Los nombres siguen las convenciones de PEP 8?
- [ ] ¿Las funciones y métodos tienen docstrings completos?
- [ ] ¿El código complejo tiene comentarios explicativos?
- [ ] No hay comentarios en exceso

### Rendimiento y Seguridad
- [ ] ¿El código evita operaciones innecesarias o costosas?
- [ ] ¿Se validan las entradas externas?
- [ ] ¿Se manejan adecuadamente los recursos (archivos, conexiones)?
- [ ] Andas buscando reducir y organizar el código, esto es prioridad. 

### Prácticas Específicas de Python
- [ ] ¿Se utilizan idiomas pythónicos (list comprehensions, generators)?
- [ ] ¿Se aprovechan las características de la biblioteca estándar?
- [ ] ¿Se utiliza correctamente el manejo de excepciones?

# Listas de Verificación para json/epyson/epyx

## Etapa 1: Revisión de Archivos de Configuración (json/epyson/epyx)

### Estructura de Datos

- [ ]  ¿La estructura JSON sigue una jerarquía lógica y clara?
- [ ]  ¿Cada clave tiene una única responsabilidad semántica?
- [ ]  ¿Se evita la duplicación de claves o valores?
- [ ]  ¿Las agrupaciones de datos son coherentes?
- [ ]  Archivos de configuración deben ser concisos: preferiblemente < 200 líneas
- [ ]  ¿Los valores siguen convenciones consistentes (camelCase, snake_case, etc.)?
- [ ]  Objetivo: minimizar redundancia y maximizar reutilización de aliases
- [ ] Se prioriza el uso del espacio horizontal sobre el vertical, cumpliendo con el PEP8
- [ ] Que los datos se organicen así:     "in": ["inch","inches", "pulgada", "pulgadas"],
    No así:     "in": [
      "inch",
      "inches",
      "pulgada",
      "pulgadas"
    ]
	Pero garantizando que no se superan los 140 caracteres por línea.
	Este es otro ejemplo, donde algo como esto:
	    "format": {
      "bg_alpha": 0.1, 
      "border": {
        "style": "solid",
        "width_px": 1.0
      },
      "line_height": 1.4,
      "size_scale": 0.95
    },
    Debería escribirse así:
		"format": {
      "bg_alpha": 0.1, "border": {"style": "solid", "width_px": 1.0},
      "line_height": 1.4, "size_scale": 0.95},
- [ ] Que los elementos de cada categoría se organicen alfanuméricamente

### Completitud y Coherencia

- [ ]  ¿El archivo cubre todos los casos de uso necesarios?
- [ ]  ¿Los aliases incluyen variaciones comunes (singular/plural, idiomas)?
- [ ]  ¿Se manejan correctamente las variaciones Unicode y ASCII?
- [ ]  ¿No hay entradas huérfanas o sin uso documentado?
- [ ]  ¿Existe metadata adecuada (version, description, last_updated)?

### Legibilidad y Mantenibilidad

- [ ]  ¿Las claves siguen nomenclatura consistente?
- [ ]  ¿Los arrays de aliases están ordenados lógicamente?
- [ ]  ¿Hay comentarios JSON (si el formato lo permite) para secciones complejas?
- [ ]  ¿El formato de indentación es consistente (2 o 4 espacios)?
- [ ]  ¿No hay comentarios innecesarios o redundantes?

### Optimización y Eficiencia

- [ ]  ¿Se eliminaron todas las duplicaciones de claves?
- [ ]  ¿Se consolidaron aliases redundantes?
- [ ]  ¿Se evitan valores hardcodeados innecesarios?
- [ ]  ¿Los aliases están normalizados (sin espacios extra, case consistency)?
- [ ]  Prioridad: **cero duplicaciones, cero redundancias, estructura mínima**

### Prácticas Específicas de json/epyson/epyx

- [ ]  ¿Se usa formato JSON válido (sin trailing commas si es JSON estricto)?
- [ ]  ¿Los arrays no tienen elementos duplicados dentro de sí mismos?
- [ ]  ¿Las claves de unidades siguen la nomenclatura canónica del sistema?
- [ ]  ¿Se aprovechan patrones para minimizar repetición (ej: prefijos comunes)?
- [ ]  ¿La validación externa (schema) confirma la estructura?
- [ ]  ¿El archivo es parse-able sin errores en el sistema de carga?

# Listas de Verificación para tests

#### Diseño

- [ ]  ¿Sigue el código los principios SOLID?
- [ ]  ¿Las clases y funciones tienen una única responsabilidad?
- [ ]  ¿El código evita la duplicación?
- [ ]  ¿Las abstracciones son adecuadas?
- [ ]  Módulos de máximo 1000 líneas. Inaceptable más de 1100. 
- [ ]  El código no tiene hardcodeado, respeta la convención epyx, epyson y json y les da prioridad.
- [ ]  Objetivo es minimizar líneas de código y módulos, optimizando procesos y sin redundancia.
- [ ] El nombre del test es representativo de su lógica.
- [ ] Homogenizar la organización de datos de entrada y salida entre tests. Buscar la organización común de información aprovechando fixtures.
- [ ] No quiero dependencias de otros archivos con data, la data requerida debe estar en el mismo módulo que los tests.
- [ ] Todo en inglés

#### Funcionalidad

- [ ]  ¿El código implementa todos los requisitos?
- [ ]  ¿Las pruebas cubren casos normales y excepcionales?
- [ ]  ¿El código maneja correctamente los casos borde?
- [ ]  No hay prints excesivos y DEBUGS.
- [ ]  Analiza el módulo abierto después de las mejoras actualizas (o creas, si no existe) un archivo log_tests.md en el que explicas y actualizas el contexto del funcionamiento, para que puedas leerlo en sesiones futuras. No es un registro de antes y después, es un resumen de potencial de la librería a partir de los tests.
- [ ] Garantiza coherencia física de los resultados del test (resultados, simplificación de unidades, unidades de acuerdo al contexto)

#### Legibilidad

- [ ]  ¿Los nombres siguen las convenciones de PEP 8?
- [ ]  ¿Las funciones y métodos tienen docstrings completos?
- [ ]  ¿El código complejo tiene comentarios explicativos?
- [ ]  No hay comentarios en exceso
- [ ] Eliminar comentarios "entre" tests. 

#### Rendimiento y Seguridad

- [ ]  ¿El código evita operaciones innecesarias o costosas?
- [ ]  ¿Se validan las entradas externas?
- [ ]  ¿Se manejan adecuadamente los recursos (archivos, conexiones)?
- [ ]  Andas buscando reducir y organizar el código, esto es prioridad.

#### Prácticas Específicas de Python

- [ ]  ¿Se utilizan idiomas pythónicos (list comprehensions, generators)?
- [ ]  ¿Se aprovechan las características de la biblioteca estándar?
- [ ]  ¿Se utiliza correctamente el manejo de excepciones?

## Conclusión

Las revisiones de código no son sólo una herramienta para encontrar errores, sino un mecanismo para mejorar continuamente la calidad del código, compartir conocimiento y fortalecer la cultura de desarrollo del equipo. Cuando se realizan con respeto, objetividad y un enfoque constructivo, las revisiones de código pueden ser uno de los procesos más valiosos en el ciclo de desarrollo de software.
## Readme.md

📋 Lista de verificación para README

- [ ] **Título del proyecto** : ¿Incluye un nombre claro y descriptivo?
- [ ] **Descripción**: ¿Explica brevemente el propósito y alcance del proyecto?
- [ ] **Tabla de contenido** _(opcional)_: ¿Está incluida para facilitar la navegación en proyectos largos?
- [ ] **Instalación**: ¿Proporciona instrucciones claras y paso a paso para instalar el proyecto?
- [ ] **Uso**: ¿Incluye ejemplos o comandos para ejecutar y utilizar el software?
- [ ] **Contribución**: ¿Describe cómo otros pueden colaborar o contribuir al proyecto?
- [ ] **Licencia**: ¿Especifica el tipo de licencia (MIT, GPL, Apache, etc.)?
- [ ] **Autores o créditos**: ¿Reconoce a los creadores, colaboradores o fuentes externas?
- [ ] **Estado del proyecto** _(opcional)_: ¿Indica si está en desarrollo, mantenimiento o abandonado?
- [ ] **Recursos adicionales** _(opcional)_: ¿Incluye enlaces útiles como documentación, demos, artículos o videos?
-

# Pendientes
Revisar si resuelve razones trigonométricas en el cálculo de expresiones, así como raíces. 




parte 1/m
highlight_columns
add_check_list
latex de las librerías de unidades
