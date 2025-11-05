"""
Test script to validate column functionality end-to-end.
"""

from ePy_docs.writers import DocumentWriter
import matplotlib.pyplot as plt
import numpy as np

def test_column_functionality():
    """Test the complete column functionality."""
    
    print("🔧 Testing column functionality...")
    
    # Create a writer with handwritten layout (2 columns for paper)
    writer = DocumentWriter(
        document_type='paper',
        layout_style='handwritten'
    )
    
    print(f"✅ Created writer - Document type: {writer.document_type}")
    
    # Add some text
    writer.add_text("Este es un documento de prueba que demuestra la funcionalidad de columnas.")
    
    # Create a simple plot
    fig, ax = plt.subplots(figsize=(6, 4))
    x = np.linspace(0, 10, 100)
    y = np.sin(x)
    ax.plot(x, y)
    ax.set_title("Test Plot")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    
    # Add plot spanning 2 columns (full width)
    print("📊 Adding full-width plot...")
    writer.add_plot(
        fig, 
        title="Full Width Plot", 
        caption="Este gráfico ocupa el ancho completo del documento",
        columns=2.0  # Span 2 columns
    )
    
    # Create another plot
    fig2, ax2 = plt.subplots(figsize=(3, 3))
    x = np.linspace(0, 5, 50)
    y = x**2
    ax2.plot(x, y, 'r-')
    ax2.set_title("Small Plot")
    
    # Add plot spanning 1 column
    print("📊 Adding single-column plot...")
    writer.add_plot(
        fig2,
        title="Single Column Plot",
        caption="Este gráfico ocupa una sola columna",
        columns=1.0  # Span 1 column
    )
    
    # Generate the document
    print("📝 Generating document...")
    result = writer.generate(
        markdown=True,
        html=True,
        pdf=False,  # Skip PDF for quick test
        qmd=True,
        output_filename="test_columns_demo"
    )
    
    print("✅ Document generated successfully!")
    print(f"📄 Generated files: {list(result.keys())}")
    
    # Check if QMD file contains proper column markdown
    if 'qmd' in result:
        qmd_path = result['qmd']
        print(f"📖 Checking QMD file: {qmd_path}")
        
        with open(qmd_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check for proper markdown format (without spaces between width and ID)
        if "{width=" in content and "#fig-" in content:
            print("✅ Found image/plot markdown in QMD")
            
            # Check for space issues
            if "} {#fig-" in content:
                print("❌ WARNING: Found spacing issue in markdown")
            else:
                print("✅ Markdown format is correct (no spacing issues)")
        
        # Show a snippet of the markdown
        lines = content.split('\n')
        plot_lines = [line for line in lines if 'width=' in line and '#fig-' in line]
        if plot_lines:
            print("📝 Plot markdown examples:")
            for line in plot_lines[:2]:  # Show first 2 examples
                print(f"   {line.strip()}")
    
    print("\n🎉 Test completed successfully!")
    return result

if __name__ == "__main__":
    test_column_functionality()