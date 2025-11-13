#!/usr/bin/env python3
"""Test add_image with specific width."""

from src.ePy_docs.writers import DocumentWriter

def test_add_image_width():
    """Test add_image with specific width."""
    print("🔍 Testing add_image with specific width...")
    
    writer = DocumentWriter()
    writer.add_content("# Width Test")
    
    try:
        # Test add_image with 3.2in width
        writer.add_image("files/viga_reforzada_propuesta_1.png", 
                        caption="Test Image", 
                        width="3.2in")
        print("✅ add_image called with width=3.2in")
        
        content_buffer = '\n'.join(writer.content_buffer)
        print(f"📄 Content buffer length: {len(content_buffer)}")
        print("=" * 40)
        print(content_buffer)
        print("=" * 40)
        
        # Check if 3.2in appears in the output
        if "3.2in" in content_buffer:
            print("✅ Width 3.2in preserved in output")
        else:
            print("❌ Width 3.2in not found in output")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_add_image_width()