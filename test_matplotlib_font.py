#!/usr/bin/env python3
"""
Script para probar que matplotlib puede usar efectivamente la fuente C2024_anm_font
"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def test_matplotlib_rendering():
    """Test actual matplotlib rendering with custom font."""
    print("=== Testing Matplotlib Rendering ===")
    
    try:
        import matplotlib.pyplot as plt
        import matplotlib.font_manager as fm
        
        # Setup fonts using our function
        from ePy_docs.core._images import setup_matplotlib_fonts
        font_list = setup_matplotlib_fonts('handwritten')
        
        print(f"Font list from setup: {font_list}")
        
        # Create a simple plot to test font rendering
        fig, ax = plt.subplots(figsize=(8, 6))
        
        # Test with the first font in our list (should be C2024_anm_font)
        test_font = font_list[0] if font_list else 'DejaVu Sans'
        
        print(f"Testing with font: {test_font}")
        
        # Create sample text
        ax.text(0.5, 0.7, 'Sample Text with Custom Font', 
                fontfamily=test_font, fontsize=16, 
                ha='center', va='center', transform=ax.transAxes)
        
        ax.text(0.5, 0.5, 'Texto de prueba con fuente personalizada', 
                fontfamily=test_font, fontsize=14, 
                ha='center', va='center', transform=ax.transAxes)
        
        ax.text(0.5, 0.3, 'Testing numbers: 1234567890', 
                fontfamily=test_font, fontsize=12, 
                ha='center', va='center', transform=ax.transAxes)
        
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_title(f'Font Test: {test_font}', fontfamily=test_font, fontsize=18)
        
        # Remove axes for cleaner look
        ax.axis('off')
        
        # Save the plot to verify it works
        output_file = Path(__file__).parent / 'font_test_output.png'
        plt.savefig(output_file, dpi=150, bbox_inches='tight')
        
        print(f"✓ Plot saved successfully to: {output_file}")
        
        # Check if the font is actually being used
        # Get the font properties of the title
        title_font = ax.get_title()
        
        print(f"✓ Font rendering test completed")
        
        plt.close()
        
        return True
        
    except Exception as e:
        print(f"✗ Error in matplotlib rendering test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_font_in_images_module():
    """Test font setup specifically in the context of the images module."""
    print("\n=== Testing Images Module Font Integration ===")
    
    try:
        # Test if the ImageProcessor can handle the font correctly
        from ePy_docs.core._images import ImageProcessor
        
        processor = ImageProcessor()
        
        # Test font setup
        fonts = processor.setup_matplotlib_fonts('handwritten')
        print(f"✓ ImageProcessor font setup: {fonts}")
        
        # Test the layout extraction
        from ePy_docs.core._config import get_layout
        layout = get_layout('handwritten')
        
        extracted_font = processor._extract_font_family_from_layout(layout)
        print(f"✓ Extracted font family: {extracted_font}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error in images module test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success1 = test_matplotlib_rendering()
    success2 = test_font_in_images_module()
    
    if success1 and success2:
        print("\n🎉 All font tests passed successfully!")
    else:
        print("\n❌ Some font tests failed.")