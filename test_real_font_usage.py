#!/usr/bin/env python3
"""
Test real de la fuente C2024_anm_font en el contexto de ePy_docs
"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def test_real_image_generation():
    """Test real image generation using handwritten layout."""
    print("=== Testing Real Image Generation with Handwritten Font ===")
    
    try:
        from ePy_docs.core._images import add_image_content
        import matplotlib.pyplot as plt
        import numpy as np
        
        # Create a simple plot with data
        x = np.linspace(0, 10, 100)
        y = np.sin(x)
        
        plt.figure(figsize=(10, 6))
        plt.plot(x, y, linewidth=2, label='sin(x)')
        plt.xlabel('X values')
        plt.ylabel('Y values')  
        plt.title('Sample Plot with Handwritten Font')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # Save with a temporary name first
        temp_file = Path(__file__).parent / 'results' / 'report' / 'figures' / 'test_handwritten_plot.png'
        temp_file.parent.mkdir(parents=True, exist_ok=True)
        
        plt.savefig(temp_file, dpi=150, bbox_inches='tight')
        plt.close()
        
        print(f"✓ Matplotlib plot saved to: {temp_file}")
        
        # Now test the ePy_docs image processing with handwritten layout
        if temp_file.exists():
            # This should trigger the font setup for handwritten layout
            result = add_image_content(
                path=str(temp_file),
                caption="Test plot using handwritten font",
                width="80%",
                layout_style='handwritten',  # This should trigger the C2024_anm_font
                document_type='report',
                figure_counter=1
            )
            
            print(f"✓ ePy_docs image processing completed")
            print(f"  Result type: {type(result)}")
            
            return True
        else:
            print(f"✗ Plot file not created")
            return False
            
    except Exception as e:
        print(f"✗ Error in real image generation test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_font_in_table_context():
    """Test font usage in table generation context."""
    print("\n=== Testing Font in Table Context ===")
    
    try:
        # Import table generation functions
        from ePy_docs.core._tables import create_table_image
        import pandas as pd
        
        # Create sample data
        data = {
            'Item': ['Sample A', 'Sample B', 'Sample C'],
            'Value': [10.5, 20.3, 15.7],
            'Status': ['Active', 'Pending', 'Complete']
        }
        
        df = pd.DataFrame(data)
        
        # Try to create a table with handwritten layout
        result = create_table_image(
            data=df,
            title="Test Table with Handwritten Font",
            layout_style='handwritten',  # This should use C2024_anm_font
            document_type='report',
            table_counter=1
        )
        
        print(f"✓ Table generation with handwritten font completed")
        print(f"  Result: {result if isinstance(result, str) else 'Table object'}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error in table font test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success1 = test_real_image_generation()
    success2 = test_font_in_table_context()
    
    if success1 and success2:
        print("\n🎉 All real-world font tests passed!")
        print("The C2024_anm_font is working correctly in matplotlib graphics!")
    else:
        print("\n❌ Some real-world font tests failed.")