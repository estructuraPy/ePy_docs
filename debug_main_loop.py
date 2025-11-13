#!/usr/bin/env python3
"""Debug the main processing loop."""

def debug_main_loop():
    """Debug the main processing loop."""
    from src.ePy_docs.writers import DocumentWriter
    
    print("🔍 Debugging main processing loop...")
    
    # Create test content
    test_content = """# Test

::: {#fig-test layout-ncol="2"}

![Image 1](files/viga_reforzada_propuesta_1.png){height="4cm"}

![Image 2](files/viga_reforzada_propuesta_2.png){height="4cm"}

Test caption
:::

Regular text."""
    
    with open('debug_main_loop.qmd', 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    try:
        # Monkey patch to add debug prints
        import src.ePy_docs.core._quarto as quarto_module
        
        original_is_figure_block_start = quarto_module._is_figure_block_start
        original_extract_figure_block = quarto_module._extract_figure_block
        original_process_figure_block = quarto_module._process_figure_block
        
        def debug_is_figure_block_start(line):
            result = original_is_figure_block_start(line)
            if result:
                print(f"🎯 Figure block detected: '{line}'")
            return result
        
        def debug_extract_figure_block(lines, start_index):
            print(f"📋 Extracting figure block from index {start_index}")
            result = original_extract_figure_block(lines, start_index)
            print(f"   -> Result: {len(result[0])} images, caption: '{result[1]}'")
            return result
        
        def debug_process_figure_block(images_data, caption, layout_config, file_path, core):
            print(f"🖼️  Processing {len(images_data)} images...")
            result = original_process_figure_block(images_data, caption, layout_config, file_path, core)
            print(f"   -> Process result: {result}")
            return result
        
        # Apply patches
        quarto_module._is_figure_block_start = debug_is_figure_block_start
        quarto_module._extract_figure_block = debug_extract_figure_block
        quarto_module._process_figure_block = debug_process_figure_block
        
        # Test with writer
        writer = DocumentWriter()
        writer.add_content("# Debug Test")
        writer.add_quarto_file('debug_main_loop.qmd', fix_image_paths=True)
        
        content_buffer = '\n'.join(writer.content_buffer)
        print(f"\n📄 Final content buffer length: {len(content_buffer)}")
        print("=" * 50)
        print(content_buffer)
        print("=" * 50)
        
        # Restore original functions
        quarto_module._is_figure_block_start = original_is_figure_block_start
        quarto_module._extract_figure_block = original_extract_figure_block
        quarto_module._process_figure_block = original_process_figure_block
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        import os
        if os.path.exists('debug_main_loop.qmd'):
            os.remove('debug_main_loop.qmd')

if __name__ == "__main__":
    debug_main_loop()