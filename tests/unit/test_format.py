"""
Unit tests for ePy_docs formatting operations.
Tests equations, references, citations, and inline formatting.
"""

import pytest
from ePy_docs.writers import ReportWriter, PaperWriter


class TestEquations:
    """Test equation formatting and LaTeX support."""
    
    def test_add_equation_basic(self):
        """Test adding a basic equation."""
        writer = ReportWriter()
        writer.add_equation("E = mc^2")
        
        content = writer.get_content()
        assert "$$E = mc^2$$" in content
    
    def test_add_equation_with_label(self):
        """Test adding equation with label."""
        writer = ReportWriter()
        writer.add_equation("F = ma", label="eq-newton")
        
        content = writer.get_content()
        assert "$$F = ma$$" in content
        assert "eq-newton" in content
    
    def test_add_equation_with_caption(self):
        """Test adding equation with caption."""
        writer = ReportWriter()
        writer.add_equation("x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}", 
                          caption="Quadratic Formula")
        
        content = writer.get_content()
        assert "x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}" in content
    
    def test_add_equation_method_chaining(self):
        """Test that add_equation returns self for chaining."""
        writer = ReportWriter()
        result = writer.add_equation("a^2 + b^2 = c^2")
        
        assert result is writer
    
    def test_add_inline_equation(self):
        """Test adding inline equation."""
        writer = ReportWriter()
        writer.add_inline_equation("x + y = z")
        
        content = writer.get_content()
        assert "$x + y = z$" in content
    
    def test_add_inline_equation_method_chaining(self):
        """Test that add_inline_equation returns self."""
        writer = ReportWriter()
        result = writer.add_inline_equation("\\alpha")
        
        assert result is writer
    
    def test_multiple_equations(self):
        """Test adding multiple equations."""
        writer = ReportWriter()
        writer.add_equation("E = mc^2", label="eq-einstein")
        writer.add_equation("F = ma", label="eq-newton")
        writer.add_equation("PV = nRT", label="eq-ideal-gas")
        
        content = writer.get_content()
        assert "mc^2" in content
        assert "ma" in content
        assert "PV = nRT" in content


class TestReferencesAndCitations:
    """Test references and citations formatting."""
    
    def test_add_reference_basic(self):
        """Test adding a basic reference."""
        writer = ReportWriter()
        writer.add_reference("eq", "eq-1")
        
        content = writer.get_content()
        assert "eq-1" in content
    
    def test_add_reference_method_chaining(self):
        """Test that add_reference returns self."""
        writer = ReportWriter()
        result = writer.add_reference("fig", "fig-1")
        
        assert result is writer
    
    def test_add_citation_basic(self):
        """Test adding a citation."""
        writer = ReportWriter()
        writer.add_citation("Smith2020")
        
        content = writer.get_content()
        assert "Smith2020" in content
    
    def test_add_citation_with_page(self):
        """Test adding citation with page number."""
        writer = ReportWriter()
        writer.add_citation("Jones2021", page="42")
        
        content = writer.get_content()
        assert "Jones2021" in content
        assert "42" in content
    
    def test_add_citation_method_chaining(self):
        """Test that add_citation returns self."""
        writer = ReportWriter()
        result = writer.add_citation("Doe2019")
        
        assert result is writer


class TestListFormatting:
    """Test list creation and formatting."""
    
    def test_add_unordered_list(self):
        """Test creating unordered list."""
        writer = ReportWriter()
        items = ["Item 1", "Item 2", "Item 3"]
        writer.add_list(items, ordered=False)
        
        content = writer.get_content()
        assert "- Item 1" in content
        assert "- Item 2" in content
        assert "- Item 3" in content
    
    def test_add_ordered_list(self):
        """Test creating ordered list."""
        writer = ReportWriter()
        items = ["First", "Second", "Third"]
        writer.add_list(items, ordered=True)
        
        content = writer.get_content()
        assert "1. First" in content
        assert "2. Second" in content
        assert "3. Third" in content
    
    def test_add_empty_list(self):
        """Test adding empty list raises ValueError."""
        writer = ReportWriter()
        
        # Should raise ValueError for empty list
        with pytest.raises(ValueError, match="cannot be empty"):
            writer.add_list([], ordered=False)
    
    def test_add_list_method_chaining(self):
        """Test that add_list returns self."""
        writer = ReportWriter()
        result = writer.add_list(["Item"], ordered=False)
        
        assert result is writer


class TestCodeFormatting:
    """Test code chunk formatting."""
    
    def test_add_chunk_python(self):
        """Test adding Python code chunk."""
        writer = ReportWriter()
        code = "x = 10\nprint(x)"
        writer.add_chunk(code, language='python')
        
        content = writer.get_content()
        assert "x = 10" in content
        assert "print(x)" in content
    
    def test_add_chunk_method_chaining(self):
        """Test that add_chunk returns self."""
        writer = ReportWriter()
        result = writer.add_chunk("code", language='python')
        
        assert result is writer
    
    def test_add_chunk_executable(self):
        """Test adding executable code chunk."""
        writer = ReportWriter()
        code = "result = 2 + 2"
        writer.add_chunk_executable(code, language='python')
        
        content = writer.get_content()
        assert "result = 2 + 2" in content
    
    def test_add_chunk_executable_method_chaining(self):
        """Test that add_chunk_executable returns self."""
        writer = ReportWriter()
        result = writer.add_chunk_executable("x = 1", language='python')
        
        assert result is writer


class TestComplexFormatting:
    """Test complex formatting scenarios."""
    
    def test_mixed_content_chaining(self):
        """Test chaining different content types."""
        writer = ReportWriter()
        
        writer.add_h1("Title") \
              .add_content("Introduction") \
              .add_equation("E = mc^2") \
              .add_list(["Point 1", "Point 2"]) \
              .add_citation("Einstein1905")
        
        content = writer.get_content()
        assert "# Title" in content
        assert "Introduction" in content
        assert "mc^2" in content
        assert "Point 1" in content
        assert "Einstein1905" in content
