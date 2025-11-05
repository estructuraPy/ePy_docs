"""
Test that imported tables/figures maintain proper consecutive numbering
"""
import sys
sys.path.append('src')

from ePy_docs import DocumentWriter
import pandas as pd
import tempfile
import os

# Create writer
writer = DocumentWriter('report', layout_style='minimal')

# Add initial content with table
writer.add_h1("Document with Mixed Content")
writer.add_text("First, a manually created table:")

data1 = pd.DataFrame({
    'Col1': ['A', 'B'],
    'Col2': [1, 2]
})
writer.add_table(data1, title="Manual Table 1")

print(f"After manual table 1: counter = {writer._core._counters['table']}")

# Import markdown with table
md_content = """
# Imported Section

| X | Y |
|---|---|
| 10 | 20 |

: Imported Table Caption
"""

with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
    f.write(md_content)
    md_path = f.name

try:
    writer.add_markdown_file(md_path, convert_tables=True)
    print(f"After imported table: counter = {writer._core._counters['table']}")
    
    # Add another manual table
    data2 = pd.DataFrame({
        'Col3': ['C', 'D'],
        'Col4': [3, 4]
    })
    writer.add_table(data2, title="Manual Table 2")
    
    print(f"After manual table 2: counter = {writer._core._counters['table']}")
    
    # Check content
    content = writer._core.get_content()
    
    # Verify consecutive numbering
    assert 'tbl-1' in content, "Missing table 1"
    assert 'tbl-2' in content, "Missing table 2"
    assert 'tbl-3' in content, "Missing table 3"
    
    print("\n✅ Consecutive numbering working correctly!")
    print(f"Total tables: {writer._core._counters['table']}")
    print(f"Generated images: {len(writer._core.generated_images)}")
    
    # Check images were generated
    assert writer._core._counters['table'] == 3, "Should have 3 tables"
    assert len(writer._core.generated_images) == 3, "Should have 3 images"
    
    print("✅ All images generated for imported and manual tables!")
    
finally:
    os.unlink(md_path)
