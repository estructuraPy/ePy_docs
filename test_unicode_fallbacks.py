from ePy_docs.writers import DocumentWriter
import pandas as pd

# Crear datos que incluyan los caracteres problemáticos
data = {
    'Descripción': ['Tabla original – Parte 1/3', 'Test con símbolos: @ # $ % & *', 'Más símbolos: : ; — /'],
    'Valores': [100, 200, 300]
}
df = pd.DataFrame(data)

writer = DocumentWriter(document_type='report', layout_style='handwritten')
writer.add_h1('Test de Caracteres Especiales')
writer.add_text('Este documento prueba caracteres como: – — / : ; @ # $ % & *')
writer.add_colored_table(df, title='Tabla con caracteres especiales – Parte 1/3')

result = writer.generate(html=False, pdf=True, output_filename='test_unicode_fallbacks')
print(f'PDF generado: {result["pdf"]}')