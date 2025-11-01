from ePy_docs.writers import DocumentWriter
import pandas as pd

# Crear datos que incluyan una amplia variedad de caracteres Unicode problemáticos
data = {
    'Texto': [
        'Table 1–1– Tabla original – Parte 1/3',
        'Símbolos: « » " " ' ' ‹ › ‚ „',
        'Guiones: - – — ― ‐ ‑ ⁃',
        'Espacios: … ․ ‧ • ‣ ⁇ ⁈ ⁉',
        'Matemáticas: ± × ÷ ° ′ ″ ‰ ‱',
        'Monedas: € £ ¥ ¢ ₹ ₽ ₿'
    ],
    'Valores': [100, 200, 300, 400, 500, 600]
}
df = pd.DataFrame(data)

writer = DocumentWriter(document_type='report', layout_style='handwritten')
writer.add_h1('Test Completo de Caracteres Unicode')
writer.add_text('Probando caracteres especiales: Table 1–1– Tabla original – Parte 1/3')
writer.add_text('Comillas: « » " " ' ' ‹ › ‚ „')
writer.add_text('Guiones y espacios: - – — … • ‣')
writer.add_text('Símbolos: ± × ÷ ° € £ ¥')
writer.add_colored_table(df, title='Tabla con caracteres Unicode – Parte 1/3')

result = writer.generate(html=False, pdf=True, output_filename='test_unicode_complete')
print(f'PDF generado: {result["pdf"]}')