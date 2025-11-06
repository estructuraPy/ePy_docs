"""
Quick debug test for rockfill tables
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from ePy_docs.writers import DocumentWriter

# Test with the exact tables from rockfill.qmd
test_content = """
# Test Document

$$FS < \\frac{\\sum F_{estabilizadoras}}{\\sum F_{desestabilizadoras}}$$

Some text before table.

| Condición de análisis | Riesgo de daños económicos y ambientales | Riesgo de pérdida de vidas |
| :-------------------- | :------------------------------------- | :------------------------ |
|                       |                                        | Bajo    | Medio   | Alto   |
| Estática              | Bajo                                    | 1,20    | 1,30    | 1,40   |
|                       | Medio                                   | 1,30    | 1,40    | 1,50   |
|                       | Alto                                    | 1,40    | 1,50    | 1,50   |
| Pseudoestático        | Bajo                                    | >1,00  | >1,00  | 1,05   |
|                       | Medio                                   | >1,00  | 1,05    | 1,10   |
|                       | Alto                                    | 1,05    | 1,10    | 1,10   |

Some text after table.
"""

import tempfile

writer = DocumentWriter(document_type='report', layout_style='minimal')

with tempfile.NamedTemporaryFile(mode='w', suffix='.qmd', delete=False, encoding='utf-8') as f:
    f.write(test_content)
    temp_file = f.name

try:
    writer.add_quarto_file(temp_file, convert_tables=True)
    content = writer.get_content()
    
    print("Content length:", len(content))
    print("\n" + "="*70)
    print("CONTENT:")
    print("="*70)
    print(content)
    print("="*70)
    
    # Generate HTML to test rendering
    output_file = "test_debug_output.html"
    writer.to_html(output_file)
    print(f"\n✓ HTML generated: {output_file}")
    
    # Check if LaTeX is in content
    if "\\frac" in content or "$$" in content:
        print("✓ LaTeX equation found in content")
    else:
        print("✗ LaTeX equation NOT found in content")
        
    # Check if table was converted
    if "![" in content:
        print("✓ Table converted to image")
    elif "|" in content:
        print("⚠ Table still in markdown format")
    else:
        print("✗ Table not found at all")
        
finally:
    os.unlink(temp_file)
