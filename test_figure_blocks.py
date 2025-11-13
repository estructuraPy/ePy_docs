#!/usr/bin/env python3
"""Test figure block processing in QMD files."""

from src.ePy_docs.writers import DocumentWriter

def test_figure_blocks():
    """Test the figure block processing functionality."""
    print("🚀 Testing figure block processing in QMD files...")
    
    try:
        # Create writer
        writer = DocumentWriter()
        writer.add_content("# Figure Block Processing Test")
        writer.add_content("This test demonstrates figure block processing.")
        
        # Import QMD with figure blocks
        print("📁 Importing QMD file with figure blocks...")
        writer.add_quarto_file("test_figure_blocks.qmd", fix_image_paths=True)
        
        print("✅ QMD file imported successfully")
        
        # Check content
        content_buffer = '\n'.join(writer.content_buffer)
        
        # Look for image processing
        image_count = content_buffer.count('![](')
        print(f"📸 Images processed: {image_count}")
        
        # Look for figure references
        if 'Propuesta 1' in content_buffer:
            print("✅ Multi-image figure block detected")
        else:
            print("⚠️  Multi-image figure block not found")
        
        # Look for layout processing
        if 'layout-ncol' in content_buffer:
            print("⚠️  Raw layout syntax still present (not processed)")
        else:
            print("✅ Layout syntax processed correctly")
        
        print(f"\n📄 Content buffer length: {len(content_buffer)} characters")
        
        # Show relevant part of content
        print("\n📖 Content preview (figure-related parts):")
        print("=" * 60)
        lines = content_buffer.split('\n')
        for i, line in enumerate(lines):
            if any(keyword in line.lower() for keyword in ['propuesta', 'fig-', 'image', 'figura']):
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

if __name__ == "__main__":
    success = test_figure_blocks()
    if success:
        print("\n🎉 Figure block processing test completed!")
    else:
        print("\n💥 Test failed!")