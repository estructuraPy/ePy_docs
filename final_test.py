#!/usr/bin/env python3
"""Test the final implementation with the original example."""

from src.ePy_docs.writers import DocumentWriter

def test_final_implementation():
    """Test the final implementation with the original example."""
    print("🚀 Testing final implementation with original example...")
    
    # Create test content matching the user's example
    test_content = '''---
title: "Test Figure Blocks"
---

# Test Document

This is a test of the Quarto figure block processing.

::: {#fig-CS layout-ncol="2" layout-nrow="1"}

![Propuesta 1](files/viga_reforzada_propuesta_1.png){#fig-round height="4cm"}

![Propuesta 2](files/viga_reforzada_propuesta_2.png){#fig-rect height="4cm"}

Propuestas de reforzamiento
:::

Regular text continues here.
'''
    
    with open('final_test.qmd', 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    try:
        writer = DocumentWriter()
        writer.add_content("# Final Implementation Test")
        
        print("📁 Importing QMD file with figure blocks...")
        writer.add_quarto_file('final_test.qmd', fix_image_paths=True)
        
        print("✅ QMD file imported successfully")
        
        # Check content
        content_buffer = '\n'.join(writer.content_buffer)
        
        # Look for expected elements
        has_propuesta1 = 'Propuesta 1' in content_buffer
        has_propuesta2 = 'Propuesta 2' in content_buffer
        has_caption = 'Propuestas de reforzamiento' in content_buffer
        has_narrow_width = '3.2in' in content_buffer
        
        print(f"✅ Propuesta 1 found: {has_propuesta1}")
        print(f"✅ Propuesta 2 found: {has_propuesta2}")
        print(f"✅ Caption found: {has_caption}")
        print(f"✅ Narrow width (3.2in) used: {has_narrow_width}")
        
        print(f"\n📄 Content buffer length: {len(content_buffer)} characters")
        
        # Show relevant parts
        print("\n📖 Content preview:")
        print("=" * 60)
        lines = content_buffer.split('\n')
        for i, line in enumerate(lines):
            if any(keyword in line.lower() for keyword in ['propuesta', 'reforzamiento', 'figura', 'figure']):
                print(f"{i:3d}: {line}")
        print("=" * 60)
        
        # Generate document
        print("\n📝 Generating document...")
        result = writer.generate(html=True, pdf=False)
        print(f"✅ Document generated: {result}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        import os
        if os.path.exists('final_test.qmd'):
            os.remove('final_test.qmd')

if __name__ == "__main__":
    success = test_final_implementation()
    if success:
        print("\n🎉 Final implementation test completed successfully!")
    else:
        print("\n💥 Test failed!")