"""
Test para verificar problemas reportados: rutas de book, bibliografía, y elementos estructurales.
"""

import pytest
import tempfile
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pathlib import Path

from ePy_docs.writers import DocumentWriter


class TestBookAndBibliography:
    """Test para book PDF y bibliografía."""
    
    def test_book_generates_with_figures(self):
        """Test que book genere correctamente con figuras."""
        writer = DocumentWriter("book", "classic")
        
        # Add content
        writer.add_h1("Chapter 1")
        writer.add_text("This is chapter 1 content.")
        
        # Add a plot
        fig, ax = plt.subplots(figsize=(6, 4))
        x = np.linspace(0, 10, 100)
        y = np.sin(x)
        ax.plot(x, y)
        ax.set_title("Sine Wave")
        writer.add_plot(fig, title="Test Plot", caption="A sine wave plot")
        
        # Add a table
        df = pd.DataFrame({
            'A': [1, 2, 3],
            'B': [4, 5, 6]
        })
        writer.add_table(df, title="Test Table")
        
        # Generate QMD only (faster for testing)
        result = writer.generate(html=False, pdf=False, qmd=True)
        qmd_path = result['qmd']
        
        # Read QMD content
        with open(qmd_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("\n--- Book QMD Content ---")
        print(content)
        print("--- End ---\n")
        
        # Check for forward slashes in image paths (not backslashes)
        assert '\\' not in content or 'usepackage' in content, \
            "Image paths should use forward slashes, not backslashes"
        
        # Check that plot and table are in content
        assert "Test Plot" in content, "Plot title should be in content"
        assert "Test Table" in content or "Tabla" in content, "Table should be in content"
        
    def test_bibliography_in_yaml(self):
        """Test que bibliography y CSL aparezcan en el YAML."""
        writer = DocumentWriter("paper", "academic")
        
        writer.add_h1("Introduction")
        writer.add_text("This is a test with citations.")
        writer.add_citation("Smith2020")
        
        # Create temporary bibliography file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.bib', delete=False, encoding='utf-8') as f:
            f.write("""
@article{Smith2020,
  author = {Smith, John},
  title = {A Test Article},
  journal = {Test Journal},
  year = {2020}
}
""")
            bib_path = f.name
        
        # Create temporary CSL file (minimal valid CSL)
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csl', delete=False, encoding='utf-8') as f:
            f.write("""<?xml version="1.0" encoding="utf-8"?>
<style xmlns="http://purl.org/net/xbiblio/csl" class="in-text" version="1.0">
  <info>
    <title>Test Style</title>
    <id>http://www.example.com/test</id>
  </info>
</style>
""")
            csl_path = f.name
        
        try:
            # Generate with bibliography
            result = writer.generate(
                html=False, 
                pdf=False, 
                qmd=True,
                bibliography_path=bib_path,
                csl_path=csl_path
            )
            qmd_path = result['qmd']
            
            # Read QMD content
            with open(qmd_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            print("\n--- Paper with Bibliography QMD ---")
            print(content)
            print("--- End ---\n")
            
            # Check YAML has bibliography (should be just the filename after copying)
            assert "bibliography:" in content or "bibliography :" in content, \
                "Bibliography path should be in YAML"
            
            # Check that the bibliography file was copied to output directory
            output_dir = Path(qmd_path).parent
            copied_bib = output_dir / Path(bib_path).name
            assert copied_bib.exists(), "Bibliography file should be copied to output directory"
            
            # Check that CSL file was copied to output directory
            copied_csl = output_dir / Path(csl_path).name
            assert copied_csl.exists(), "CSL file should be copied to output directory"
            
            # Check citation is in content
            assert "@Smith2020" in content, "Citation should be in content"
            
        finally:
            # Cleanup
            try:
                Path(bib_path).unlink()
            except:
                pass
            try:
                Path(csl_path).unlink()
            except:
                pass
    
    def test_structural_elements_dont_use_column_span(self):
        """Test que elementos estructurales (ToC, headers) no reciban column_span."""
        writer = DocumentWriter("paper", "academic")
        
        writer.add_h1("Chapter Title")
        writer.add_h2("Section Title")
        writer.add_text("Some content here.")
        
        # Add a plot with column_span
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.plot([1, 2, 3], [1, 2, 3])
        writer.add_plot(fig, title="Test Plot", column_span=2)
        
        result = writer.generate(html=False, pdf=False, qmd=True)
        qmd_path = result['qmd']
        
        with open(qmd_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Headers should NOT have column classes
        lines = content.split('\n')
        for line in lines:
            if line.startswith('#'):  # Header lines
                assert '.column-' not in line, "Headers should not have column classes"
        
        # But the plot should have column class
        assert '.column-' in content, "Plot should have column class"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
