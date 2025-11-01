"""
Test script to verify LaTeX font configuration works for handwritten layout PDF generation.
"""

from ePy_docs.writers import DocumentWriter

# Initialize writer with handwritten layout
writer = DocumentWriter(document_type='report', layout_style='handwritten')

# Add some content
writer.add_h1("Test Document with Handwritten Font")
writer.add_text("This is a test document to verify that the handwritten font configuration works correctly.")
writer.add_text("Special characters that might need fallback fonts: @ : ; % $ # & *")

# Try to generate PDF (this should trigger LaTeX compilation)
try:
    result = writer.generate(html=False, pdf=True, output_filename="test_handwritten_font")
    print(f"✓ PDF generated successfully: {result}")
except Exception as e:
    print(f"✗ Error generating PDF: {e}")
    import traceback
    traceback.print_exc()