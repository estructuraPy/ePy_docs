"""
Ejemplo completo demostrando los DOS tipos de referencias en ePy_docs:
1. Referencias cruzadas internas (tablas, figuras, ecuaciones en el documento)
2. Citas bibliográficas externas (desde archivo .bib)
"""

from ePy_docs import DocumentWriter
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from pathlib import Path

# Obtener rutas a archivos de bibliografía
package_root = Path(__file__).parent.parent / 'src' / 'ePy_docs'
bibliography_file = package_root / 'config' / 'assets' / 'bibliography' / 'references.bib'
csl_file = package_root / 'config' / 'assets' / 'csl' / 'ieee.csl'

# Crear documento
writer = DocumentWriter("paper", layout_style="academic")

writer.add_h1("Ejemplo Completo de Referencias")

# ============================================================================
# PARTE 1: REFERENCIAS CRUZADAS INTERNAS
# ============================================================================

writer.add_h2("1. Referencias Cruzadas Internas")

writer.add_text("""
Las referencias cruzadas permiten referenciar elementos dentro del mismo documento.
Primero creamos los elementos con labels, luego los referenciamos.
""")

writer.add_h3("1.1 Crear Elementos con Labels")

# Crear figura con label
fig1, ax1 = plt.subplots(figsize=(6, 4))
x = np.linspace(0, 10, 100)
ax1.plot(x, np.sin(x), label='Sine')
ax1.plot(x, np.cos(x), label='Cosine')
ax1.set_xlabel('x')
ax1.set_ylabel('y')
ax1.legend()
ax1.grid(True)
writer.add_plot(fig1, title="Funciones Trigonométricas", 
               caption="Gráfico de funciones seno y coseno", 
               label="fig-trig")

# Crear tabla con label
df = pd.DataFrame({
    'Elemento': ['Viga', 'Columna', 'Losa'],
    'Esfuerzo (MPa)': [250, 350, 180],
    'Factor Seguridad': [1.5, 2.0, 1.8]
})
writer.add_table(df, title="Resultados Estructurales", label="tbl-structural")

# Crear ecuación con label
writer.add_equation(
    r"\sigma = \frac{F}{A}",
    caption="Esfuerzo normal",
    label="eq-stress"
)

writer.add_h3("1.2 Referenciar Elementos Creados")

writer.add_text("Ahora podemos referenciar estos elementos en el texto:")

writer.add_text("Como se observa en ")
writer.add_reference_to_element("figure", "fig-trig")
writer.add_text(", las funciones trigonométricas presentan comportamiento periódico.")

writer.add_text("Los valores de esfuerzo mostrados en ")
writer.add_reference_to_element("table", "tbl-structural")
writer.add_text(" cumplen con los requisitos de diseño.")

writer.add_text("Utilizando ")
writer.add_reference_to_element("equation", "eq-stress")
writer.add_text(", podemos calcular el esfuerzo en cada elemento.")

# ============================================================================
# PARTE 2: CITAS BIBLIOGRÁFICAS EXTERNAS
# ============================================================================

writer.add_h2("2. Citas Bibliográficas Externas")

writer.add_text("""
Las citas bibliográficas referencian fuentes externas desde un archivo .bib.
Hay dos formas de citarlas:
""")

writer.add_h3("2.1 Método 1: Sintaxis @key (Recomendado)")

writer.add_text("""
La forma más simple es usar la sintaxis @key directamente en el texto:
""")

# Citas entre paréntesis
writer.add_text("""
El código sísmico [@CSCR2010_14] establece los requisitos de diseño para estructuras.
Los criterios de diseño de concreto se especifican en [@ACI318_19].
""")

# Citas narrativas
writer.add_text("""
Según @AISC360_22, el diseño de estructuras de acero debe considerar múltiples factores.
El trabajo de @ACI318_19 proporciona las bases para el diseño de concreto reforzado.
""")

# Múltiples citas
writer.add_text("""
Los códigos de diseño [@CSCR2010_14; @ACI318_19; @AISC360_22] establecen requisitos
específicos para garantizar la seguridad estructural.
""")

writer.add_h3("2.2 Método 2: add_reference_citation() (Programático)")

writer.add_text("También se puede usar el método programático:")

writer.add_text("El diseño por viento ")
writer.add_reference_citation("LDpV2023")
writer.add_text(" considera velocidades regionales.")

writer.add_text("Las cimentaciones deben diseñarse según ")
writer.add_reference_citation("CCCR2009", page="15-20")
writer.add_text(" para garantizar estabilidad.")

# ============================================================================
# PARTE 3: COMBINANDO AMBOS TIPOS
# ============================================================================

writer.add_h2("3. Combinando Referencias Internas y Citas Bibliográficas")

writer.add_text("""
En documentos técnicos, es común combinar ambos tipos de referencias:
""")

writer.add_text("Los resultados experimentales presentados en ")
writer.add_reference_to_element("table", "tbl-structural")
writer.add_text(" fueron comparados con los requisitos del código sísmico [@CSCR2010_14]. ")
writer.add_text("El análisis siguió la metodología de @ACI318_19, aplicando ")
writer.add_reference_to_element("equation", "eq-stress")
writer.add_text(" para cada elemento estructural.")

writer.add_h2("4. Ventajas de Cada Método")

writer.add_list([
    "Referencias internas: Permiten navegación automática en PDFs",
    "Citas @key: Sintaxis más natural y concisa",
    "Método add_reference_citation(): Mayor control programático",
    "Archivo .bib: Gestión centralizada de referencias bibliográficas"
], ordered=False)

# Generar documento
result = writer.generate(
    html=True,
    pdf=True,
    qmd=True,
    output_filename="referencias_completo",
    bibliography_path=str(bibliography_file),
    csl_path=str(csl_file)
)

print("\n=== Documento Generado ===")
for format_type, path in result.items():
    if path:
        print(f"{format_type.upper()}: {path}")

print("\n=== Tipos de Referencias Utilizadas ===")
print("✓ Referencias cruzadas internas:")
print("  - Figura 1 (fig-trig)")
print("  - Tabla 1 (tbl-structural)")  
print("  - Ecuación 1 (eq-stress)")
print("\n✓ Citas bibliográficas externas:")
print("  - @CSCR2010_14, @ACI318_19, @AISC360_22")
print("  - @LDpV2023, @CCCR2009")
print("\nAbre el PDF para ver las referencias cruzadas funcionando!")
