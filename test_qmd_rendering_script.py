"""Test QMD rendering with corporate layout."""

from src.ePy_docs.writers import DocumentWriter

print("=" * 70)
print("Testing QMD rendering with corporate layout")
print("=" * 70)

# Create writer with corporate layout
writer = DocumentWriter(layout_style='corporate')

# Add header
writer.add_content("# Prueba de Renderizado QMD - Layout Corporativo")

# Import the QMD file
print("\n📁 Importing QMD file...")
writer.add_quarto_file('test_qmd_rendering.qmd', fix_image_paths=True)

# Generate document
print("\n📝 Generating document...")
result = writer.generate()

print(f"\n✅ Document generated!")
print(f"📄 QMD: {result.get('qmd')}")
print(f"📝 HTML: {result.get('html')}")

# Check content buffer
print("\n" + "=" * 70)
print("Checking content buffer for text rendering...")
print("=" * 70)

# Read generated QMD to verify content
with open(result.get('qmd'), 'r', encoding='utf-8') as f:
    content = f.read()
    
# Check for specific content
checks = [
    ("Introducción heading", "# Introducción" in content),
    ("Metodología heading", "# Metodología" in content),
    ("LaTeX math", "$115 kgf/cm^{2}$" in content or "$115 kgf/cm^2$" in content),
    ("References", "@CSCR2010_14" in content),
    ("Table reference", "@tbl-nucleos" in content),
    ("Figure reference", "@fig-original" in content),
    ("Normal text", "El proyecto corresponde" in content),
]

print("\n✓ Content verification:")
for check_name, result in checks:
    status = "✅" if result else "❌"
    print(f"  {status} {check_name}: {result}")

print("\n" + "=" * 70)
print("Preview of generated content (first 1000 chars):")
print("=" * 70)
print(content[:1000])
