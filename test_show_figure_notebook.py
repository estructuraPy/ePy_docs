"""
Test script to verify show_figure=True works in Jupyter notebooks.
Run this in a Jupyter notebook to see the table image displayed inline.
"""

from ePy_docs.writers import DocumentWriter
import pandas as pd

# Create sample data
data = {
    'Esfuerzo (MPa)': [0.0, 10.5, 21.0, 31.5, 42.0],
    'Deformación (%)': [0.0, 0.5, 1.0, 1.5, 2.0],
    'Material': ['Acero', 'Acero', 'Acero', 'Acero', 'Acero']
}
df = pd.DataFrame(data)

# Initialize writer with handwritten layout
writer = DocumentWriter(document_type='report', layout_style='handwritten')

# Add table with show_figure=True to display in notebook
print("Generando tabla con show_figure=True...")
writer.add_colored_table(
    df, 
    title='Tabla convertida a Imperial', 
    show_figure=True  # This will display the image immediately in Jupyter
)

print("\n✓ Tabla generada exitosamente")
print(f"✓ Archivo guardado en: {writer.generated_images[-1]}")
print("\nLa imagen debería aparecer arriba de este mensaje si estás en un notebook Jupyter.")
