#!/usr/bin/env python3
"""
Test real evidence of layout differences in generated documents
"""
from ePy_docs.writers import DocumentWriter
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import tempfile
import os

def test_layout_evidence():
    """Generate actual documents to prove layouts work differently"""
    
    # Create test data
    df = pd.DataFrame({
        'Item': ['A', 'B', 'C'],
        'Value': [10, 20, 30],
        'Score': [0.8, 0.6, 0.9]
    })
    
    # Create a simple plot
    fig, ax = plt.subplots(figsize=(6, 4))
    x = np.array([1, 2, 3])
    y = np.array([10, 20, 30])
    ax.plot(x, y, 'o-')
    ax.set_title('Test Plot')
    ax.set_xlabel('X values')
    ax.set_ylabel('Y values')
    
    # Test different layouts
    layouts_to_test = ['professional', 'creative', 'minimal', 'handwritten']
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        for layout in layouts_to_test:
            print(f"\n=== Testing {layout} layout ===")
            
            try:
                # Create writer
                writer = DocumentWriter('report', layout)
                
                # Add content
                writer.add_h1(f"Test Document - {layout.title()}")
                writer.add_text(f"This document uses the {layout} layout style.")
                writer.add_table(df, title=f"Sample Table ({layout})")
                writer.add_plot(fig, title=f"Sample Plot ({layout})")
                
                # Generate HTML to check actual output
                result = writer.generate(
                    output_filename=f"{layout}_evidence",
                    html=True,
                    pdf=False,
                    qmd=True
                )
                
                if 'html' in result:
                    html_path = Path(result['html'])
                    qmd_path = Path(result['qmd'])
                    
                print(f"SUCCESS Generated: {html_path.name}")
                print(f"SUCCESS Generated: {qmd_path.name}")                    # Read and analyze QMD content
                    qmd_content = qmd_path.read_text(encoding='utf-8')
                    
                    # Look for layout-specific elements
                    layout_indicators = []
                    
                    # Check for font family references
                    if 'sans_professional' in qmd_content or 'professional' in qmd_content.lower():
                        layout_indicators.append("font: professional")
                    elif 'sans_creative' in qmd_content or 'creative' in qmd_content.lower():
                        layout_indicators.append("font: creative")
                    elif 'sans_minimal' in qmd_content or 'minimal' in qmd_content.lower():
                        layout_indicators.append("font: minimal")
                    elif 'handwritten' in qmd_content.lower():
                        layout_indicators.append("font: handwritten")
                    
                    # Check for color references or CSS
                    if 'color' in qmd_content.lower():
                        layout_indicators.append("colors: detected")
                    
                    # Check for specific styling
                    if 'margin' in qmd_content.lower():
                        layout_indicators.append("margins: detected")
                    
                    # Read HTML content for more evidence
                    if html_path.exists():
                        html_content = html_path.read_text(encoding='utf-8')
                        
                        # Look for CSS variables that should be different
                        if '--primary-color' in html_content:
                            layout_indicators.append("CSS variables: found")
                        
                        # Extract actual color values if present
                        import re
                        color_matches = re.findall(r'--primary-color:\s*([^;]+);', html_content)
                        if color_matches:
                            layout_indicators.append(f"primary color: {color_matches[0].strip()}")
                    
                    print(f"   Layout indicators: {', '.join(layout_indicators) if layout_indicators else 'NONE FOUND'}")
                    
                    # Show first few lines of QMD for evidence
                    qmd_lines = qmd_content.split('\n')[:15]
                    print("   QMD Header:")
                    for i, line in enumerate(qmd_lines, 1):
                        if line.strip():
                            print(f"      {i:2}: {line}")
                        if i >= 10:
                            break
                
            except Exception as e:
                print(f"X {layout} failed: {e}")
                import traceback
                print(f"   Error details: {traceback.format_exc()}")
            
            plt.close('all')  # Clean up plots

if __name__ == "__main__":
    test_layout_evidence()