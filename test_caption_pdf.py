from ePy_docs.writers import DocumentWriter
import pandas as pd

data = {'A': [1, 2], 'B': [3, 4]}
df = pd.DataFrame(data)

writer = DocumentWriter(document_type='report', layout_style='handwritten')
writer.add_h1('Test Caption PDF')
writer.add_colored_table(df, title='Tabla Sin Caption Duplicado')

result = writer.generate(html=False, pdf=True, output_filename='test_caption_pdf')
print(f'PDF generado: {result["pdf"]}')