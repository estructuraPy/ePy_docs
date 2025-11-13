#!/usr/bin/env python3
"""Direct test of figure block processing logic."""

def test_figure_processing_logic():
    """Test the figure processing logic step by step."""
    from src.ePy_docs.writers import DocumentWriter
    from src.ePy_docs.core._quarto import _process_figure_block
    
    print("🔍 Testing figure processing logic directly...")
    
    # Create test data
    images_data = [
        {
            'alt_text': 'Image 1',
            'path': 'files/viga_reforzada_propuesta_1.png',
            'config': {'height': '4cm'}
        },
        {
            'alt_text': 'Image 2', 
            'path': 'files/viga_reforzada_propuesta_2.png',
            'config': {'height': '4cm'}
        }
    ]
    caption = "Test caption"
    layout_config = {'ncol': 2}
    file_path = "debug_test.qmd"
    
    # Create writer and get core
    writer = DocumentWriter()
    core = writer._core if hasattr(writer, '_core') else writer
    
    print("📋 Writer created, calling _process_figure_block...")
    
    # Call the function directly
    try:
        result = _process_figure_block(images_data, caption, layout_config, file_path, core)
        print(f"✅ _process_figure_block returned: {result}")
        
        # Check content buffer
        content_buffer = '\n'.join(core.content_buffer)
        print(f"📄 Content buffer length: {len(content_buffer)}")
        print("=" * 40)
        print(content_buffer)
        print("=" * 40)
        
    except Exception as e:
        print(f"❌ Error in _process_figure_block: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_figure_processing_logic()