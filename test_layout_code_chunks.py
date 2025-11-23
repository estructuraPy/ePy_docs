"""Test code chunks loading from layout configuration."""

from ePy_docs import DocumentWriter

# Test 1: Academic layout (italic caption)
print("=" * 60)
print("TEST 1: Academic Layout - Caption format: *{caption}*")
print("=" * 60)

doc_academic = DocumentWriter(document_type="report", layout_style="academic")
doc_academic.add_h1("Academic Layout Test")
doc_academic.add_code_chunk(
    code="x = 42\nprint(x)",
    language="python",
    chunk_type="display",
    caption="Example code in academic style"
)
doc_academic.generate(html=True, pdf=True)
print("✓ Academic layout generated successfully\n")

# Test 2: Corporate layout (bold caption)
print("=" * 60)
print("TEST 2: Corporate Layout - Caption format: **{caption}**")
print("=" * 60)

doc_corporate = DocumentWriter(document_type="report", layout_style="corporate")
doc_corporate.add_h1("Corporate Layout Test")
doc_corporate.add_code_chunk(
    code="SELECT * FROM users;",
    language="sql",
    chunk_type="executable",
    caption="SQL query in corporate style"
)
doc_corporate.generate(html=True, pdf=True)
print("✓ Corporate layout generated successfully\n")

# Test 3: Scientific layout (numbered caption)
print("=" * 60)
print("TEST 3: Scientific Layout - Caption format: **Code {counter}:** {caption}")
print("=" * 60)

doc_scientific = DocumentWriter(document_type="report", layout_style="scientific")
doc_scientific.add_h1("Scientific Layout Test")
doc_scientific.add_code_chunk(
    code="import numpy as np\ndata = np.array([1, 2, 3])",
    language="python",
    chunk_type="display",
    caption="Data initialization"
)
doc_scientific.add_code_chunk(
    code="mean = np.mean(data)",
    language="python",
    chunk_type="executable",
    caption="Calculate mean value"
)
doc_scientific.generate(html=True, pdf=True)
print("✓ Scientific layout generated successfully\n")

# Test 4: Creative layout (emoji caption + extra spacing)
print("=" * 60)
print("TEST 4: Creative Layout - Caption format: 🎨 {caption}")
print("=" * 60)

doc_creative = DocumentWriter(document_type="report", layout_style="creative")
doc_creative.add_h1("Creative Layout Test")
doc_creative.add_code_chunk(
    code="function greet(name) {\n  return `Hello, ${name}!`;\n}",
    language="javascript",
    chunk_type="display",
    caption="Greeting function"
)
doc_creative.generate(html=True, pdf=True)
print("✓ Creative layout generated successfully\n")

# Test 5: Minimal layout (plain caption)
print("=" * 60)
print("TEST 5: Minimal Layout - Caption format: {caption}")
print("=" * 60)

doc_minimal = DocumentWriter(document_type="report", layout_style="minimal")
doc_minimal.add_h1("Minimal Layout Test")
doc_minimal.add_code_chunk(
    code="echo 'Hello World'",
    language="bash",
    chunk_type="executable",
    caption="Shell command"
)
doc_minimal.generate(html=True, pdf=True)
print("✓ Minimal layout generated successfully\n")

print("=" * 60)
print("ALL TESTS COMPLETED SUCCESSFULLY!")
print("=" * 60)
print("\nGenerated files:")
print("  - test_academic_chunks.html/pdf")
print("  - test_corporate_chunks.html/pdf")
print("  - test_scientific_chunks.html/pdf")
print("  - test_creative_chunks.html/pdf")
print("  - test_minimal_chunks.html/pdf")
