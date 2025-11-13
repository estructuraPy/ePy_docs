#!/usr/bin/env python3
"""Test add_image method directly."""

from src.ePy_docs.writers import DocumentWriter

def test_add_image_directly():
    """Test add_image method directly."""
    print("🔍 Testing add_image method directly...")
    
    try:
        writer = DocumentWriter()
        writer.add_content("# Test Direct Image Addition")
        
        # Test 1: Try adding image that doesn't exist
        try:
            writer.add_image("files/viga_reforzada_propuesta_1.png", caption="Test Image", height="1.6in")
            print("✅ add_image method called successfully")
        except Exception as e:
            print(f"❌ add_image failed: {e}")
        
        # Check content buffer
        content_buffer = '\n'.join(writer.content_buffer)
        print(f"📄 Content buffer length: {len(content_buffer)}")
        print("=" * 40)
        print(content_buffer)
        print("=" * 40)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_add_image_directly()