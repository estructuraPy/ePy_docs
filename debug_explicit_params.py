#!/usr/bin/env python3
"""Debug with explicit parameters."""

def debug_with_explicit_params():
    """Debug with explicit parameters."""
    from src.ePy_docs.writers import DocumentWriter
    
    print("🔍 Testing with explicit parameters...")
    
    # Create test content
    test_content = """# Test

::: {#fig-test layout-ncol="2"}

![Image 1](files/viga_reforzada_propuesta_1.png){height="4cm"}

![Image 2](files/viga_reforzada_propuesta_2.png){height="4cm"}

Test caption
:::

Regular text."""
    
    with open('debug_explicit.qmd', 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    try:
        writer = DocumentWriter()
        writer.add_content("# Debug Test")
        
        print("📋 Calling add_quarto_file with explicit fix_image_paths=True...")
        writer.add_quarto_file('debug_explicit.qmd', 
                              fix_image_paths=True, 
                              convert_tables=True, 
                              execute_code_blocks=False)  # Disable code execution for simpler test
        
        content_buffer = '\n'.join(writer.content_buffer)
        print(f"\n📄 Final content buffer length: {len(content_buffer)}")
        
        # Check if figure block content appears anywhere
        if "::: {#fig-test" in content_buffer:
            print("⚠️  Raw figure block still present")
        elif "Image 1" in content_buffer or "Image 2" in content_buffer:
            print("✅ Image processing detected")
        else:
            print("❌ No trace of images found")
        
        print("=" * 50)
        print(content_buffer)
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        import os
        if os.path.exists('debug_explicit.qmd'):
            os.remove('debug_explicit.qmd')

if __name__ == "__main__":
    debug_with_explicit_params()