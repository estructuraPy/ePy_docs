"""
Comprehensive tests for DocumentWriter methods.
Each test ensures all possible parameters are tested.
"""

import pytest
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import tempfile
import shutil
from ePy_docs.writers import DocumentWriter


class TestDocumentWriterComprehensive:
    """Comprehensive tests for all DocumentWriter methods with all parameters."""

    @pytest.fixture
    def writer(self):
        """Create a fresh DocumentWriter instance for each test."""
        return DocumentWriter("report", "professional")

    @pytest.fixture
    def sample_dataframe(self):
        """Create sample DataFrame for table tests."""
        return pd.DataFrame({
            'ID': [1, 2, 3, 4, 5],
            'Name': ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve'],
            'Score': [95, 87, 92, 88, 91],
            'Category': ['A', 'B', 'A', 'C', 'B'],
            'Date': pd.date_range('2024-01-01', periods=5),
            'Internal_Code': ['X1', 'X2', 'X3', 'X4', 'X5']
        })

    @pytest.fixture
    def sample_plot(self):
        """Create sample matplotlib figure for plot tests."""
        fig, ax = plt.subplots(figsize=(8, 6))
        x = np.linspace(0, 10, 100)
        y = np.sin(x)
        ax.plot(x, y, label='sin(x)')
        ax.set_xlabel('x')
        ax.set_ylabel('y')
        ax.legend()
        ax.set_title('Sample Plot')
        return fig

    @pytest.fixture
    def temp_image_file(self):
        """Create temporary image file for image tests."""
        temp_dir = Path(tempfile.mkdtemp())
        img_path = temp_dir / "test_image.png"
        
        # Create a simple test image
        fig, ax = plt.subplots(figsize=(4, 3))
        ax.text(0.5, 0.5, 'Test Image', ha='center', va='center', fontsize=16)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        fig.savefig(img_path, dpi=100, bbox_inches='tight')
        plt.close(fig)
        
        yield str(img_path)
        
        # Cleanup
        if temp_dir.exists():
            shutil.rmtree(temp_dir)

    @pytest.fixture
    def temp_markdown_file(self):
        """Create temporary markdown file for file import tests."""
        temp_dir = Path(tempfile.mkdtemp())
        md_path = temp_dir / "test.md"
        
        md_content = """# Test Markdown
        
This is a test markdown file with:

- Bullet point 1
- Bullet point 2

## Subsection

Some text with **bold** and *italic* formatting.

| Column 1 | Column 2 |
|----------|----------|
| Value 1  | Value 2  |
| Value 3  | Value 4  |
"""
        md_path.write_text(md_content)
        
        yield str(md_path)
        
        # Cleanup
        if temp_dir.exists():
            shutil.rmtree(temp_dir)

    @pytest.fixture
    def temp_quarto_file(self):
        """Create temporary quarto file for file import tests."""
        temp_dir = Path(tempfile.mkdtemp())
        qmd_path = temp_dir / "test.qmd"
        
        qmd_content = """---
title: "Test Document"
author: "Test Author"
format: html
---

# Test Quarto

This is a test quarto file.

## Analysis Section

```{python}
import numpy as np
x = np.array([1, 2, 3, 4, 5])
print(f"Mean: {np.mean(x)}")
```

Some analysis text here.
"""
        qmd_path.write_text(qmd_content)
        
        yield str(qmd_path)
        
        # Cleanup
        if temp_dir.exists():
            shutil.rmtree(temp_dir)

    def test_add_table_all_parameters(self, writer, sample_dataframe):
        """Test add_table with all possible parameter combinations."""
        
        # Test with all parameters as None (defaults)
        result = writer.add_table(
            df=sample_dataframe,
            title=None,
            show_figure=True,
            columns=None,
            max_rows_per_table=None,
            hide_columns=None,
            filter_by=None,
            sort_by=None,
            width_inches=None
        )
        assert result is writer
        
        # Test with all parameters specified
        result = writer.add_table(
            df=sample_dataframe,
            title="Test Table",
            show_figure=False,
            columns=2.0,
            max_rows_per_table=3,
            hide_columns=['ID', 'Internal_Code'],
            filter_by={'Category': 'A'},
            sort_by=['Score', 'Name'],
            width_inches=6.5
        )
        assert result is writer
        
        # Test with single string hide_columns
        result = writer.add_table(
            df=sample_dataframe,
            title="Hidden Column Test",
            hide_columns='Internal_Code',
            sort_by='Score'
        )
        assert result is writer
        
        # Test with max_rows_per_table as list
        result = writer.add_table(
            df=sample_dataframe,
            title="Split Table Test",
            max_rows_per_table=[2, 2, 1],
            filter_by={'Score': [95, 87, 92]}
        )
        assert result is writer
        
        # Test with columns as list
        result = writer.add_table(
            df=sample_dataframe,
            title="Multi-Column Test",
            columns=[6.0, 4.0, 8.0]
        )
        assert result is writer

    def test_add_colored_table_all_parameters(self, writer, sample_dataframe):
        """Test add_colored_table with all possible parameter combinations."""
        
        # Test with all parameters as None (defaults)
        result = writer.add_colored_table(
            df=sample_dataframe,
            title=None,
            show_figure=True,
            columns=None,
            highlight_columns=None,
            palette_name=None,
            max_rows_per_table=None,
            hide_columns=None,
            filter_by=None,
            sort_by=None,
            width_inches=None
        )
        assert result is writer
        
        # Test with all parameters specified
        result = writer.add_colored_table(
            df=sample_dataframe,
            title="Colored Test Table",
            show_figure=False,
            columns=1.5,
            highlight_columns=['Score'],
            palette_name='blues',
            max_rows_per_table=4,
            hide_columns=['ID'],
            filter_by={'Category': ['A', 'B']},
            sort_by='Score',
            width_inches=7.0
        )
        assert result is writer
        
        # Test with multiple highlight columns
        result = writer.add_colored_table(
            df=sample_dataframe,
            title="Multi-Highlight Test",
            highlight_columns=['Score', 'ID'],
            palette_name='reds'
        )
        assert result is writer
        
        # Test with different palettes
        for palette in ['greens', 'oranges', 'purples', 'minimal', 'professional']:
            result = writer.add_colored_table(
                df=sample_dataframe,
                title=f"Palette {palette}",
                highlight_columns='Score',
                palette_name=palette
            )
            assert result is writer

    def test_add_plot_all_parameters(self, writer, sample_plot):
        """Test add_plot with all possible parameter combinations."""
        
        # Test with all parameters as None (defaults)
        result = writer.add_plot(
            fig=sample_plot,
            title=None,
            caption=None,
            source=None,
            columns=None,
            palette_name=None
        )
        assert result is writer
        
        # Test with all parameters specified
        result = writer.add_plot(
            fig=sample_plot,
            title="Test Plot",
            caption="This is a test plot caption",
            source="Generated by test",
            columns=2.0,
            palette_name='blues'
        )
        assert result is writer
        
        # Test with columns as list
        result = writer.add_plot(
            fig=sample_plot,
            title="Multi-Column Plot",
            columns=[6.0, 4.0, 8.0],
            palette_name='reds'
        )
        assert result is writer
        
        # Test different palettes
        for palette in ['greens', 'minimal', 'professional']:
            result = writer.add_plot(
                fig=sample_plot,
                title=f"Plot {palette}",
                palette_name=palette
            )
            assert result is writer

    def test_add_image_all_parameters(self, writer, temp_image_file):
        """Test add_image with all possible parameter combinations."""
        
        # Test with all parameters as None (defaults)
        result = writer.add_image(
            path=temp_image_file,
            caption=None,
            width=None,
            columns=None,
            alt_text=None,
            responsive=True
        )
        assert result is writer
        
        # Test with all parameters specified
        result = writer.add_image(
            path=temp_image_file,
            caption="Test Image Caption",
            width="80%",
            columns=1.5,
            alt_text="Alternative text for accessibility",
            responsive=False
        )
        assert result is writer
        
        # Test with columns as list
        result = writer.add_image(
            path=temp_image_file,
            caption="Multi-Column Image",
            columns=[6.0, 4.0, 8.0],
            responsive=True
        )
        assert result is writer
        
        # Test with different width formats
        for width in ["100%", "6in", "15cm"]:
            result = writer.add_image(
                path=temp_image_file,
                caption=f"Width {width}",
                width=width
            )
            assert result is writer

    def test_add_equation_all_parameters(self, writer):
        """Test add_equation with all possible parameter combinations."""
        
        # Test with all parameters as None (defaults)
        result = writer.add_equation(
            latex_code="E = mc^2",
            caption=None,
            label=None
        )
        assert result is writer
        
        # Test with all parameters specified
        result = writer.add_equation(
            latex_code="\\frac{-b \\pm \\sqrt{b^2-4ac}}{2a}",
            caption="Quadratic formula",
            label="eq-quadratic"
        )
        assert result is writer
        
        # Test various equation types
        equations = [
            ("\\sum_{i=1}^{n} x_i", "Summation", "eq-sum"),
            ("\\int_{0}^{\\infty} e^{-x} dx", "Integral", "eq-integral"),
            ("\\begin{matrix} a & b \\\\ c & d \\end{matrix}", "Matrix", "eq-matrix")
        ]
        
        for latex, caption, label in equations:
            result = writer.add_equation(latex_code=latex, caption=caption, label=label)
            assert result is writer

    def test_add_chunk_all_parameters(self, writer):
        """Test add_chunk with all possible parameter combinations."""
        
        # Test with all parameters as None (defaults)
        result = writer.add_chunk(
            code="print('Hello, World!')",
            language='python',
            caption=None
        )
        assert result is writer
        
        # Test with all parameters specified
        result = writer.add_chunk(
            code="def factorial(n):\\n    return 1 if n <= 1 else n * factorial(n-1)",
            language='python',
            caption="Recursive factorial function"
        )
        assert result is writer
        
        # Test different languages (only valid ones)
        language_tests = [
            ("SELECT * FROM users WHERE active = 1;", "sql", "SQL Query"),
            ("function hello() { console.log('Hello'); }", "javascript", "JavaScript Function"),
            ("#!/bin/bash\\necho 'Hello from bash'", "bash", "Bash Script"),
            ("library(ggplot2)\\nplot(1:10)", "r", "R Code"),
            ("import numpy as np\\nprint('Hello')", "python", "Python Code")
        ]
        
        for code, lang, caption in language_tests:
            result = writer.add_chunk(code=code, language=lang, caption=caption)
            assert result is writer

    def test_add_chunk_executable_all_parameters(self, writer):
        """Test add_chunk_executable with all possible parameter combinations."""
        
        # Test with all parameters as None (defaults)
        result = writer.add_chunk_executable(
            code="import math\\nprint(f'Pi = {math.pi}')",
            language='python',
            caption=None
        )
        assert result is writer
        
        # Test with all parameters specified
        result = writer.add_chunk_executable(
            code="x = [1, 2, 3, 4, 5]\\nprint(f'Sum: {sum(x)}, Mean: {sum(x)/len(x)}')",
            language='python',
            caption="Simple statistics calculation"
        )
        assert result is writer

    def test_add_callout_all_parameters(self, writer):
        """Test add_callout with all possible parameter combinations."""
        
        # Test with all parameters as None (defaults)
        result = writer.add_callout(
            content="This is a basic note",
            type="note",
            title=None
        )
        assert result is writer
        
        # Test with all parameters specified
        result = writer.add_callout(
            content="This is a custom warning with title",
            type="warning",
            title="Custom Warning Title"
        )
        assert result is writer
        
        # Test all callout types
        callout_types = [
            ("note", "Note content", "Custom Note"),
            ("tip", "Helpful tip content", "Pro Tip"),
            ("warning", "Warning content", "Important Warning"),
            ("error", "Error content", "Critical Error"),
            ("success", "Success content", "Success Message"),
            ("caution", "Caution content", "Proceed with Caution"),
            ("important", "Important content", "Important Information"),
            ("information", "Information content", "Additional Info"),
            ("advice", "Advice content", "Expert Advice")
        ]
        
        for callout_type, content, title in callout_types:
            result = writer.add_callout(content=content, type=callout_type, title=title)
            assert result is writer

    def test_all_callout_shortcuts(self, writer):
        """Test all callout shortcut methods with parameters."""
        
        callout_methods = [
            ('add_note', "Note content"),
            ('add_tip', "Tip content"),
            ('add_warning', "Warning content"),
            ('add_error', "Error content"),
            ('add_success', "Success content"),
            ('add_caution', "Caution content"),
            ('add_important', "Important content"),
            ('add_information', "Information content"),
            ('add_recommendation', "Recommendation content"),
            ('add_advice', "Advice content"),
            ('add_risk', "Risk content")
        ]
        
        for method_name, content in callout_methods:
            method = getattr(writer, method_name)
            
            # Test with title=None (default)
            result = method(content=content, title=None)
            assert result is writer
            
            # Test with custom title
            result = method(content=content, title=f"Custom {method_name.replace('add_', '').title()}")
            assert result is writer

    def test_add_list_all_parameters(self, writer):
        """Test add_list with all possible parameter combinations."""
        
        items = ["First item", "Second item", "Third item"]
        
        # Test unordered list (default)
        result = writer.add_list(items=items, ordered=False)
        assert result is writer
        
        # Test ordered list
        result = writer.add_list(items=items, ordered=True)
        assert result is writer

    def test_add_reference_all_parameters(self, writer):
        """Test add_reference with all possible parameter combinations."""
        
        # Test with custom_text=None (default)
        result = writer.add_reference(
            ref_type="table",
            ref_id="tbl-1",
            custom_text=None
        )
        assert result is writer
        
        # Test with all parameters specified
        result = writer.add_reference(
            ref_type="figure",
            ref_id="fig-stress",
            custom_text="the stress analysis plot"
        )
        assert result is writer
        
        # Test different reference types
        ref_tests = [
            ("table", "tbl-results", "the results table"),
            ("tbl", "tbl-summary", "Table Summary"),
            ("figure", "fig-diagram", "the system diagram"),
            ("fig", "fig-plot", "Figure Plot"),
            ("equation", "eq-einstein", "Einstein's equation"),
            ("eq", "eq-formula", "the formula")
        ]
        
        for ref_type, ref_id, custom_text in ref_tests:
            result = writer.add_reference(ref_type=ref_type, ref_id=ref_id, custom_text=custom_text)
            assert result is writer

    def test_add_citation_all_parameters(self, writer):
        """Test add_citation with all possible parameter combinations."""
        
        # Test with page=None (default)
        result = writer.add_citation(
            citation_key="Einstein1905",
            page=None
        )
        assert result is writer
        
        # Test with all parameters specified
        result = writer.add_citation(
            citation_key="Smith2020",
            page="127"
        )
        assert result is writer
        
        # Test different page formats
        page_tests = [
            ("Johnson2018", "42"),
            ("Brown2019", "15-20"),
            ("Davis2021", "123-125"),
            ("Wilson2022", "p. 56")
        ]
        
        for citation_key, page in page_tests:
            result = writer.add_citation(citation_key=citation_key, page=page)
            assert result is writer

    def test_add_markdown_file_all_parameters(self, writer, temp_markdown_file):
        """Test add_markdown_file with all possible parameter combinations."""
        
        # Test with all parameters as defaults
        result = writer.add_markdown_file(
            file_path=temp_markdown_file,
            fix_image_paths=True,
            convert_tables=True
        )
        assert result is writer
        
        # Test with all parameters specified
        result = writer.add_markdown_file(
            file_path=temp_markdown_file,
            fix_image_paths=False,
            convert_tables=False
        )
        assert result is writer
        
        # Test different parameter combinations
        param_combinations = [
            (True, False),   # fix_image_paths=True, convert_tables=False
            (False, True),   # fix_image_paths=False, convert_tables=True
        ]
        
        for fix_images, convert_tables in param_combinations:
            result = writer.add_markdown_file(
                file_path=temp_markdown_file,
                fix_image_paths=fix_images,
                convert_tables=convert_tables
            )
            assert result is writer

    def test_add_quarto_file_all_parameters(self, writer, temp_quarto_file):
        """Test add_quarto_file with all possible parameter combinations."""
        
        # Test with all parameters as defaults
        result = writer.add_quarto_file(
            file_path=temp_quarto_file,
            include_yaml=False,
            fix_image_paths=True,
            convert_tables=True
        )
        assert result is writer
        
        # Test with all parameters specified
        result = writer.add_quarto_file(
            file_path=temp_quarto_file,
            include_yaml=True,
            fix_image_paths=False,
            convert_tables=False
        )
        assert result is writer
        
        # Test different parameter combinations
        param_combinations = [
            (True, True, False),   # include_yaml=True, fix_image_paths=True, convert_tables=False
            (False, False, True),  # include_yaml=False, fix_image_paths=False, convert_tables=True
            (True, False, True),   # include_yaml=True, fix_image_paths=False, convert_tables=True
        ]
        
        for include_yaml, fix_images, convert_tables in param_combinations:
            result = writer.add_quarto_file(
                file_path=temp_quarto_file,
                include_yaml=include_yaml,
                fix_image_paths=fix_images,
                convert_tables=convert_tables
            )
            assert result is writer

    def test_generate_all_parameters(self, writer):
        """Test generate with all possible parameter combinations."""
        
        # Add some content first
        writer.add_h1("Test Document")
        writer.add_text("This is test content.")
        
        # Test with all parameters as defaults
        result = writer.generate(
            markdown=False,
            html=True,
            pdf=True,
            qmd=True,
            tex=False,
            output_filename=None
        )
        assert isinstance(result, dict)
        
        # Create new writer for next test (since generate can only be called once)
        writer2 = DocumentWriter("report", "professional")
        writer2.add_h1("Test Document 2")
        writer2.add_text("This is test content 2.")
        
        # Test with all parameters specified
        result = writer2.generate(
            markdown=True,
            html=False,
            pdf=False,
            qmd=False,
            tex=True,
            output_filename="CustomReport"
        )
        assert isinstance(result, dict)

    def test_simple_methods_all_parameters(self, writer):
        """Test simple methods that have only basic parameters."""
        
        # Test add_content
        result = writer.add_content("Raw content")
        assert result is writer
        
        # Test header methods
        for i, method_name in enumerate(['add_h1', 'add_h2', 'add_h3', 'add_h4', 'add_h5', 'add_h6'], 1):
            method = getattr(writer, method_name)
            result = method(f"Header Level {i}")
            assert result is writer
        
        # Test add_text
        result = writer.add_text("Paragraph text with **bold** and *italic*")
        assert result is writer
        
        # Test add_unordered_list
        result = writer.add_unordered_list(["Item 1", "Item 2", "Item 3"])
        assert result is writer
        
        # Test add_ordered_list
        result = writer.add_ordered_list(["First", "Second", "Third"])
        assert result is writer
        
        # Test add_inline_equation
        result = writer.add_inline_equation("x^2 + y^2 = z^2")
        assert result is writer
        
        # Test get_content
        content = writer.get_content()
        assert isinstance(content, str)
        assert len(content) > 0

    def test_constructor_all_parameters(self):
        """Test DocumentWriter constructor with all possible parameter combinations."""
        
        # Test with all parameters as None (defaults)
        writer = DocumentWriter(
            document_type="report",
            layout_style=None,
            project_file=None,
            language=None,
            columns=None
        )
        assert writer is not None
        
        # Test with all parameters specified
        writer = DocumentWriter(
            document_type="paper",
            layout_style="academic",
            project_file="custom_project.json",
            language="es",
            columns=2
        )
        assert writer is not None
        
        # Test different document types
        for doc_type in ["report", "paper", "book", "presentations"]:
            writer = DocumentWriter(document_type=doc_type)
            assert writer is not None
        
        # Test different layout styles
        for layout in ["professional", "creative", "minimal", "handwritten", "classic", "scientific", "technical", "academic", "corporate"]:
            writer = DocumentWriter(document_type="report", layout_style=layout)
            assert writer is not None
        
        # Test different languages
        for lang in ["en", "es", "fr", "de", "it", "pt"]:
            writer = DocumentWriter(language=lang)
            assert writer is not None
        
        # Test different column numbers
        for cols in [1, 2, 3]:
            writer = DocumentWriter(columns=cols)
            assert writer is not None

    def test_method_chaining_comprehensive(self, writer, sample_dataframe, sample_plot, temp_image_file):
        """Test comprehensive method chaining with all methods."""
        
        result = (writer
                 .add_h1("Comprehensive Document")
                 .add_text("Introduction paragraph")
                 .add_h2("Data Section")
                 .add_table(sample_dataframe, title="Sample Data", hide_columns=['ID'])
                 .add_colored_table(sample_dataframe, title="Colored Data", highlight_columns=['Score'], palette_name='blues')
                 .add_h2("Analysis Section")
                 .add_plot(sample_plot, title="Analysis Plot", caption="Plot caption")
                 .add_image(temp_image_file, caption="Sample Image", responsive=True)
                 .add_h2("Mathematical Section")
                 .add_equation("E = mc^2", caption="Energy equation", label="eq-energy")
                 .add_text("As shown in ")
                 .add_reference("equation", "eq-energy")
                 .add_h2("Code Section")
                 .add_chunk("print('Hello, World!')", language="python", caption="Hello World")
                 .add_chunk_executable("import math\\nprint(math.pi)", language="python")
                 .add_h2("Lists and Callouts")
                 .add_unordered_list(["Point 1", "Point 2", "Point 3"])
                 .add_ordered_list(["Step 1", "Step 2", "Step 3"])
                 .add_note("This is an important note", title="Note")
                 .add_warning("This is a warning", title="Warning")
                 .add_tip("This is a helpful tip")
                 .add_h2("References")
                 .add_citation("Einstein1905", page="42")
                 .add_text("End of document"))
        
        assert result is writer
        
        # Verify content was added
        content = writer.get_content()
        assert "Comprehensive Document" in content
        assert "Sample Data" in content
        assert "Hello World" in content
        assert len(content) > 1000  # Ensure substantial content was added

    def test_edge_cases_and_special_values(self, writer, sample_dataframe):
        """Test edge cases and special parameter values."""
        
        # Test empty DataFrame
        empty_df = pd.DataFrame()
        with pytest.raises((ValueError, TypeError)):
            writer.add_table(empty_df)
        
        # Test single-row DataFrame
        single_row_df = pd.DataFrame({'A': [1], 'B': [2]})
        result = writer.add_table(single_row_df, title="Single Row")
        assert result is writer
        
        # Test very long title
        long_title = "A" * 200
        result = writer.add_table(sample_dataframe, title=long_title)
        assert result is writer
        
        # Test special characters in title
        special_title = "Título con áccéntos y símbolos: @#$%^&*()"
        result = writer.add_table(sample_dataframe, title=special_title)
        assert result is writer
        
        # Test extreme column values  
        result = writer.add_table(sample_dataframe, columns=0.5)  # Narrow but reasonable
        assert result is writer
        
        result = writer.add_table(sample_dataframe, columns=2.0)  # Wide but reasonable  
        assert result is writer
        
        # Test simple max_rows_per_table
        result = writer.add_table(sample_dataframe, max_rows_per_table=3)  # Split table
        assert result is writer
        
        # Test nonexistent columns in hide_columns
        result = writer.add_table(sample_dataframe, hide_columns=['NonexistentColumn'])
        assert result is writer
        
        # Test simple filter_by
        simple_filter = {'Category': 'A'}
        result = writer.add_table(sample_dataframe, filter_by=simple_filter)
        assert result is writer

if __name__ == "__main__":
    pytest.main([__file__, "-v"])