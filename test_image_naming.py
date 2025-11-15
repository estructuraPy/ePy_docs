#!/usr/bin/env python3
"""
Test image naming standardization.
"""

import matplotlib.pyplot as plt
import pandas as pd
import shutil
from pathlib import Path

# Add src to path
import sys
sys.path.insert(0, 'src')

from ePy_docs import DocumentWriter

def test_image_naming():
    """Test that images are saved only with figure_ prefix and no duplications."""
    
    # Clear any existing test results
    test_dir = Path('results/test_image_naming')
    if test_dir.exists():
        shutil.rmtree(test_dir)
    
    # Create a writer
    writer = DocumentWriter(
        layout_style='creative', 
        document_type="report"
    )
    
    # Create test plots
    fig1, ax1 = plt.subplots(figsize=(8, 6))
    ax1.plot([1, 2, 3, 4], [1, 4, 2, 3])
    ax1.set_title('Test Plot 1')
    
    fig2, ax2 = plt.subplots(figsize=(8, 6))
    ax2.bar(['A', 'B', 'C'], [10, 20, 15])
    ax2.set_title('Test Plot 2')
    
    # Add plots to writer
    writer.add_plot(fig1, title="First Plot", caption="First test plot")
    writer.add_plot(fig2, title="Second Plot", caption="Second test plot")
    
    # Generate document
    paths = writer.generate("test_image_naming")
    
    # Check the figures directory
    figures_dir = Path('results/test_image_naming/figures')
    if figures_dir.exists():
        print("Files in figures directory:")
        for file in sorted(figures_dir.iterdir()):
            if file.is_file():
                print(f"  {file.name}")
        
        # Check for proper naming
        figure_files = list(figures_dir.glob('figure_*.png'))
        other_files = [f for f in figures_dir.iterdir() if f.is_file() and not f.name.startswith('figure_')]
        
        print(f"\nFigure files (should be 2): {len(figure_files)}")
        for f in figure_files:
            print(f"  ✓ {f.name}")
            
        if other_files:
            print(f"\nOther files (should be 0): {len(other_files)}")
            for f in other_files:
                print(f"  ✗ {f.name}")
        else:
            print("\nNo unexpected files found! ✓")
    else:
        print("No figures directory found!")
    
    # Close figures
    plt.close(fig1)
    plt.close(fig2)

if __name__ == "__main__":
    test_image_naming()