from src.ePy_docs.writers import DocumentWriter

test_content = """
# Prueba Completa de Fuentes Handwritten

## 1. Texto con Letras y Puntuación

Este es un texto normal con puntuación. Contiene puntos, comas, guiones-medios y otros signos. ¿Funciona la interrogación? ¡Y la exclamación también!

Las letras deben verse en estilo manuscrito (C2024_anm_font si está disponible).
La puntuación TAMBIÉN debe verse manuscrita (no en Times Roman o Arial estándar).

## 2. Alfabeto Completo

ABCDEFGHIJKLMNOPQRSTUVWXYZ
abcdefghijklmnopqrstuvwxyz
0123456789

## 3. Puntuación y Símbolos

Punto: .
Coma: ,
Punto y coma: ;
Dos puntos: :
Guion corto: -
Guion medio: –
Guion largo: —
Paréntesis: ( )
Corchetes: [ ]
Llaves: { }
Comillas: " "
Apóstrofo: '
Interrogación: ¿?
Exclamación: ¡!

## 4. Símbolos Griegos (Cursive Fallback)

- Alpha: α
- Beta: β
- Gamma: γ
- Delta: δ
- Pi: π
- Sigma: σ
- Theta: θ
- Omega: ω

## 5. Símbolos Matemáticos

- Menor igual: ≤
- Mayor igual: ≥
- Más-menos: ±
- Multiplicación: ×
- División: ÷
- Infinito: ∞

## 6. Diacríticos Españoles

- Vocales con tilde: á é í ó ú
- Mayúsculas con tilde: Á É Í Ó Ú
- Eñe: ñ Ñ
- Diéresis: ü Ü

---

## VERIFICACIÓN VISUAL

**Lo que DEBE verse manuscrito:**
✓ TODAS las letras (A-Z, a-z)
✓ TODOS los números (0-9)
✓ TODA la puntuación (. , ; : - — – etc.)
✓ Símbolos griegos en cursiva (α β π σ)
✓ Diacríticos (á é í ó ú ñ)

**Lo que NO debe aparecer:**
✗ Times New Roman
✗ Arial estándar
✗ DejaVu Sans
✗ Cualquier fuente "normal" no manuscrita

**Si ves fuentes estándar en puntos/comas/guiones = FALLA**
"""

# Generar HTML
writer_html = DocumentWriter(document_type="report", layout_style="handwritten")
writer_html.add_text(test_content)

result_html = writer_html.generate(
    html=True,
    pdf=False,
    markdown=False,
    qmd=False,
    output_filename="PRUEBA_HANDWRITTEN_HTML"
)

print("="*60)
print("HTML GENERADO")
print("="*60)
print(f"Archivo: {result_html.get('html')}")
print("\nAbre en navegador y verifica que TODO se vea manuscrito")

# Generar PDF
writer_pdf = DocumentWriter(document_type="report", layout_style="handwritten")
writer_pdf.add_text(test_content)

result_pdf = writer_pdf.generate(
    html=False,
    pdf=True,
    markdown=False,
    qmd=True,
    output_filename="PRUEBA_HANDWRITTEN_PDF"
)

print("\n" + "="*60)
print("PDF GENERADO")
print("="*60)
print(f"Archivo: {result_pdf.get('pdf')}")
print("\nAbre el PDF y verifica que TODO se vea manuscrito")
print("\nSi ves Times/Arial en puntuacion, el fallback NO funciona")
print("="*60)
