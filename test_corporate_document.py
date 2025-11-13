"""Test document generation with brand font (Helvetica)."""

from src.ePy_docs.writers import DocumentWriter

# Create a document with corporate layout (uses brand font)
writer = DocumentWriter(layout_style='corporate')

# Add content
writer.add_content("# Documento Corporativo")
writer.add_content("""
Este documento utiliza la fuente **Helvetica corporativa** desde la ubicación configurada.

## Características

- Fuente: `helvetica_lt_std_compressed.otf`
- Ubicación: Dropbox corporativo
- Fallback: Arial

## Texto de Prueba

Este es un texto de prueba para verificar que la fuente se carga correctamente desde la ubicación especificada. La fuente debería verse como Helvetica Compressed.

### Símbolos Matemáticos

Algunos símbolos griegos: α, β, γ, δ, σ, π, Δ, Σ, Ω

### Estilos de Texto

- **Negrita** (Bold)
- *Cursiva* (Italic)
- ***Negrita Cursiva*** (Bold Italic)

## Conclusión

Si este documento se genera correctamente, significa que la configuración de la fuente está funcionando.
""")

# Generate document
print("🚀 Generating document with brand font...")
result = writer.generate()
print(f"✅ Document generated successfully!")
print(f"📄 QMD: {result.get('qmd')}")
print(f"📝 HTML: {result.get('html')}")

print("\n" + "=" * 60)
print("Next steps:")
print("1. Open the generated QMD file")
print("2. Render to PDF using Quarto")
print("3. Verify the font is Helvetica Compressed")
print("=" * 60)
