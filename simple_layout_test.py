#!/usr/bin/env python3
"""
Simple test to show layout differences in CSS
"""
from ePy_docs.writers import DocumentWriter
import pandas as pd

def test_simple_layouts():
    print("\n=== LAYOUT EVIDENCE TEST ===")
    
    layouts = ['professional', 'creative', 'minimal', 'handwritten']
    
    for layout in layouts:
        print(f"\n--- Testing {layout} layout ---")
        
        try:
            # Create writer with specific layout
            writer = DocumentWriter(layout_style=layout)
            
            # Add some content
            writer.add_h1(f"Test {layout}")
            writer.add_text("Sample text")
            
            # Add simple table
            df = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
            writer.add_table(df)
            
            # Generate and get styles
            result = writer.generate(output_filename=f"test_{layout}", html=True, qmd=False, pdf=False)
            
            if 'html' in result:
                html_file = result['html']
                print(f"   Generated: {html_file}")
                
                # Read and analyze CSS from the HTML file
                with open(html_file, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                
                # Look for specific color patterns in styles
                import re
                
                # Find CSS variables
                css_vars = re.findall(r'--([^:]+):\s*([^;]+);', html_content)
                color_vars = [(var, val) for var, val in css_vars if 'color' in var.lower() or 'background' in var.lower()]
                
                if color_vars:
                    print("   CSS color variables found:")
                    for var, val in color_vars[:5]:  # Show first 5
                        print(f"     --{var}: {val}")
                
                # Look for specific RGB values
                rgb_colors = re.findall(r'rgb\(\s*(\d+),\s*(\d+),\s*(\d+)\s*\)', html_content)
                if rgb_colors:
                    print("   RGB colors found:")
                    for rgb in rgb_colors[:3]:  # Show first 3
                        print(f"     rgb({rgb[0]}, {rgb[1]}, {rgb[2]})")
                
                # Look for font family references
                fonts = re.findall(r'font-family:\s*([^;]+);', html_content)
                if fonts:
                    print(f"   Font families: {fonts[0] if fonts else 'None found'}")
                    
        except Exception as e:
            print(f"   ERROR: {e}")

if __name__ == "__main__":
    test_simple_layouts()