#!/usr/bin/env python3
"""Debug figure block processing step by step."""

from src.ePy_docs.writers import DocumentWriter

def debug_figure_processing():
    """Debug figure block processing."""
    print("🔍 Debugging figure block processing...")
    
    # Create simple test content
    test_content = """# Test

::: {#fig-test layout-ncol="2"}

![Image 1](files/viga_reforzada_propuesta_1.png){height="4cm"}

![Image 2](files/viga_reforzada_propuesta_2.png){height="4cm"}

Test caption
:::

Regular text."""
    
    with open('debug_test.qmd', 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    try:
        print("📄 Test content created")
        
        # Test the functions directly
        from src.ePy_docs.core._quarto import _is_figure_block_start, _extract_figure_block
        
        lines = test_content.split('\n')
        print(f"📝 Content has {len(lines)} lines")
        
        for i, line in enumerate(lines):
            is_fig_start = _is_figure_block_start(line)
            print(f"Line {i}: '{line}' -> Figure start: {is_fig_start}")
            
            if is_fig_start:
                print("🎯 Processing figure block...")
                images_data, caption, layout_config, next_i = _extract_figure_block(lines, i)
                print(f"   Images found: {len(images_data)}")
                print(f"   Caption: {caption}")
                print(f"   Layout: {layout_config}")
                print(f"   Next index: {next_i}")
                
                for j, img in enumerate(images_data):
                    print(f"   Image {j+1}: {img}")
                break
        
        # Now test with writer
        print("\n📋 Testing with DocumentWriter...")
        writer = DocumentWriter()
        writer.add_quarto_file('debug_test.qmd', fix_image_paths=True)
        
        content_buffer = '\n'.join(writer.content_buffer)
        print(f"Content buffer length: {len(content_buffer)}")
        print("Content preview:")
        print("=" * 40)
        print(content_buffer)
        print("=" * 40)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        import os
        if os.path.exists('debug_test.qmd'):
            os.remove('debug_test.qmd')

if __name__ == "__main__":
    debug_figure_processing()