from ePy_docs.writers import DocumentWriter
import pandas as pd

# Crear datos que incluyan específicamente los caracteres problemáticos reportados
data = {
    'Tabla': ['Table 1', 'Tabla original', 'Parte 1/3'],
    'Descripción': ['Test con – guión', 'Más símbolos: comillas', 'Final prueba'],
    'Valores': [100, 200, 300]
}
df = pd.DataFrame(data)

writer = DocumentWriter(document_type='report', layout_style='handwritten')
writer.add_h1('Test Específico de Caracteres Problemáticos')
writer.add_text('Caracteres específicos reportados: Table 1–1– Tabla original – Parte 1/3')
writer.add_text('Más caracteres: comillas y guiones — – /')
writer.add_colored_table(df, title='Table 1–1– Tabla original – Parte 1/3')

result = writer.generate(html=False, pdf=True, output_filename='test_specific_chars')
print(f'PDF generado: {result["pdf"]}')