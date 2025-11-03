"""
Real-world example: Graph generation with handwritten fonts.
This demonstrates the exact workflow you should use in your code.
"""

import matplotlib.pyplot as plt
import numpy as np
from ePy_docs import setup_matplotlib_fonts, apply_fonts_to_plot


def generate_engineering_plot():
    """
    Example of generating an engineering plot with handwritten layout.
    This is the pattern you should follow in your actual code.
    """
    
    # IMPORTANT: Setup fonts FIRST and get the font_list
    font_list = setup_matplotlib_fonts('handwritten')
    print(f"Using fonts: {font_list}")
    
    # Create your plot as usual
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Sample engineering data
    load = np.linspace(0, 100, 50)  # Load in kN
    displacement = 0.5 * load + np.random.normal(0, 2, 50)  # mm
    
    # Create the plot
    ax.plot(load, displacement, 'o-', linewidth=2, markersize=4, 
            label='Test Data', color='#2E86AB')
    
    # Add labels and title
    ax.set_xlabel('Load (kN)')
    ax.set_ylabel('Displacement (mm)')
    ax.set_title('Load-Displacement Relationship')
    ax.legend()
    ax.grid(True, alpha=0.3, linestyle='--')
    
    # CRITICAL STEP: Apply fonts directly to the plot elements
    # This is what makes it work! Same as tables.
    apply_fonts_to_plot(ax, font_list)
    
    # Save
    output_path = 'results/report/engineering_example_handwritten.png'
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"✅ Plot saved to: {output_path}")
    print("   All text elements now use handwritten font with proper fallbacks")
    return output_path


def generate_multi_subplot_example():
    """
    Example with multiple subplots - shows apply_fonts_to_figure usage.
    """
    
    from ePy_docs import apply_fonts_to_figure
    
    # Setup fonts
    font_list = setup_matplotlib_fonts('handwritten')
    
    # Create figure with multiple subplots
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 10))
    
    # Subplot 1: Line plot
    x = np.linspace(0, 10, 100)
    ax1.plot(x, np.sin(x))
    ax1.set_xlabel('X axis')
    ax1.set_ylabel('Y axis')
    ax1.set_title('Sine Wave')
    ax1.grid(True, alpha=0.3)
    
    # Subplot 2: Bar chart
    categories = ['A', 'B', 'C', 'D']
    values = [23, 45, 56, 78]
    ax2.bar(categories, values)
    ax2.set_xlabel('Category')
    ax2.set_ylabel('Value')
    ax2.set_title('Bar Chart')
    ax2.grid(True, alpha=0.3, axis='y')
    
    # Subplot 3: Scatter
    x_scatter = np.random.randn(50)
    y_scatter = np.random.randn(50)
    ax3.scatter(x_scatter, y_scatter, alpha=0.6)
    ax3.set_xlabel('Variable X')
    ax3.set_ylabel('Variable Y')
    ax3.set_title('Scatter Plot')
    ax3.grid(True, alpha=0.3)
    
    # Subplot 4: Histogram
    data = np.random.normal(0, 1, 1000)
    ax4.hist(data, bins=30, alpha=0.7, color='steelblue')
    ax4.set_xlabel('Value')
    ax4.set_ylabel('Frequency')
    ax4.set_title('Histogram')
    ax4.grid(True, alpha=0.3, axis='y')
    
    # Add figure title
    fig.suptitle('Engineering Analysis Results', fontsize=16, fontweight='bold')
    
    # Apply fonts to the entire figure (all subplots at once)
    apply_fonts_to_figure(fig, font_list)
    
    # Adjust layout and save
    plt.tight_layout()
    output_path = 'results/report/multi_subplot_handwritten.png'
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"✅ Multi-subplot figure saved to: {output_path}")
    return output_path


def main():
    print("="*70)
    print("REAL-WORLD EXAMPLES: Handwritten Font Application")
    print("="*70)
    print("\nThese examples show exactly how to use fonts in your code.\n")
    
    # Single plot example
    print("\n1. Single Plot Example:")
    print("-" * 70)
    generate_engineering_plot()
    
    # Multi-subplot example
    print("\n2. Multi-Subplot Example:")
    print("-" * 70)
    generate_multi_subplot_example()
    
    print("\n" + "="*70)
    print("PATTERN TO FOLLOW IN YOUR CODE:")
    print("="*70)
    print("""
    from ePy_docs import setup_matplotlib_fonts, apply_fonts_to_plot
    
    # 1. Setup fonts FIRST
    font_list = setup_matplotlib_fonts('handwritten')
    
    # 2. Create your plot
    fig, ax = plt.subplots()
    ax.plot(x, y)
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_title('Title')
    
    # 3. Apply fonts to plot elements
    apply_fonts_to_plot(ax, font_list)
    
    # 4. Save
    plt.savefig('output.png')
    """)
    print("="*70)


if __name__ == '__main__':
    main()
