"""
Unified Document Writers API - PURE DELEGATION LAYER

CONSTITUTIONAL PRINCIPLE: TRANSPARENCY DIMENSION - DELEGATION KINGDOM
This API is a PURE INTERFACE that only delegates to specialized modules.
ZERO business logic exists here - only method routing and parameter passing.

Architecture:
- DocumentWriter: Unified interface for all document types (report/paper)
- Explicit document_type parameter for clarity
- NO logic, NO validation, NO conditionals - pure delegation only
- All business logic delegated to core/* modules

Performance:
- Lazy imports for faster startup
- All validation delegated to core._validators module
- All logic delegated to core modules
"""

from typing import List, Dict, Any
import pandas as pd


class DocumentWriter:
    """
    Unified document writer - PURE DELEGATION to core modules.
    
    Usage:
        writer = DocumentWriter("report", layout_style="classic")
        writer = DocumentWriter("paper", layout_style="academic")
        writer = DocumentWriter("report", project_file="custom_project.json")
    """
    
    def __init__(self, document_type: str = "report", layout_style: str = None, project_file: str = None):
        """Initialize - PURE DELEGATION to core text module.
        
        Args:
            document_type: Type of document ('report' or 'paper'). Default 'report'.
            layout_style: Layout style name. If None, uses default for document type.
            project_file: Path to custom project configuration file (JSON or .epyson).
                         If None, uses default project.epyson from config directory.
                         This file overrides project-specific settings like title, author, etc.
        """
        from ePy_docs.core._text import DocumentWriterCore
        self._core = DocumentWriterCore(document_type, layout_style, project_file)
    
    @property
    def document_type(self) -> str: return self._core.document_type
    
    @property 
    def layout_style(self) -> str: return self._core.layout_style
        
    @property
    def output_dir(self) -> str: return self._core.output_dir
        
    @property
    def config(self) -> Dict[str, Any]: return self._core.config
        
    @property
    def table_counter(self) -> int: return self._core.table_counter
    
    @property
    def figure_counter(self) -> int: return self._core.figure_counter
    
    @property
    def note_counter(self) -> int: return self._core.note_counter
    
    @property
    def content_buffer(self) -> List[str]: return self._core.content_buffer
        
    @property
    def generated_images(self) -> List[str]: return self._core.generated_images
    
    def add_content(self, content: str) -> 'DocumentWriter':
        """Add content."""
        self._core.add_content(content)
        return self
    
    def get_content(self) -> str:
        """Get content."""
        return self._core.get_content()
    
    def add_h1(self, text: str) -> 'DocumentWriter':
        """Add H1 header."""
        self._core.add_h1(text)
        return self
    
    def add_h2(self, text: str) -> 'DocumentWriter':
        """Add H2 header."""
        self._core.add_h2(text)
        return self
    
    def add_h3(self, text: str) -> 'DocumentWriter':
        """Add H3 header."""
        self._core.add_h3(text)
        return self
    
    def add_h4(self, text: str) -> 'DocumentWriter':
        """Add H4 header."""
        self._core.add_h4(text)
        return self
    
    def add_h5(self, text: str) -> 'DocumentWriter':
        """Add H5 header."""
        self._core.add_h5(text)
        return self
    
    def add_h6(self, text: str) -> 'DocumentWriter':
        """Add H6 header."""
        self._core.add_h6(text)
        return self
    
    def add_text(self, content: str) -> 'DocumentWriter':
        """Add text."""
        self._core.add_text(content)
        return self
    
    def add_list(self, items: List[str], ordered: bool = False) -> 'DocumentWriter':
        """Add list."""
        self._core.add_list(items, ordered)
        return self
    
    def add_unordered_list(self, items: List[str]) -> 'DocumentWriter':
        """Add unordered list."""
        self._core.add_unordered_list(items)
        return self
    
    def add_ordered_list(self, items: List[str]) -> 'DocumentWriter':
        """Add ordered list."""
        self._core.add_ordered_list(items)
        return self
    
    def add_table(self, df: pd.DataFrame, title: str = None, 
                  show_figure: bool = True, **kwargs) -> 'DocumentWriter':
        """Add table.
        
        Args:
            df: DataFrame containing table data.
            title: Optional table title/caption.
            show_figure: If True, displays the generated table image immediately in Jupyter notebooks.
                        Useful for interactive development. Default True for immediate visualization.
                        Note: The table is always included in the final document regardless of this setting.
            **kwargs: Additional options (max_rows_per_table, hide_columns, filter_by, sort_by, etc.).
            
        Returns:
            Self for method chaining.
        """
        self._core.add_table(df, title, show_figure, **kwargs)
        return self
    
    def add_colored_table(self, df: pd.DataFrame, title: str = None, 
                          show_figure: bool = True, **kwargs) -> 'DocumentWriter':
        """Add colored table with optional column highlighting.
        
        Args:
            df: DataFrame containing table data.
            title: Optional table title/caption.
            show_figure: If True, displays the generated table image immediately in Jupyter notebooks.
                        Useful for interactive development. Default True for immediate visualization.
                        Note: The table is always included in the final document regardless of this setting.
            **kwargs: Additional options:
                - highlight_columns: Column name(s) to highlight with color gradient. 
                                   Can be a single string or list of strings (e.g., "Esfuerzo" or ["Force", "Moment"])
                - palette_name: Color palette for highlighting (e.g., 'blues', 'reds', 'greens')
                - max_rows_per_table: Split table into multiple parts if too large
            
        Returns:
            Self for method chaining.
        """
        self._core.add_colored_table(df, title, show_figure, **kwargs)
        return self
    
    def add_equation(self, latex_code: str, caption: str = None, label: str = None) -> 'DocumentWriter':
        """Add equation."""
        self._core.add_equation(latex_code, caption, label)
        return self
    
    def add_inline_equation(self, latex_code: str) -> 'DocumentWriter':
        """Add inline equation."""
        self._core.add_inline_equation(latex_code)
        return self
    
    def add_callout(self, content: str, type: str = "note", title: str = None) -> 'DocumentWriter':
        """Add callout."""
        self._core.add_callout(content, type, title)
        return self
    
    def add_note(self, content: str, title: str = None) -> 'DocumentWriter':
        """Add note."""
        self._core.add_note(content, title)
        return self
    
    def add_tip(self, content: str, title: str = None) -> 'DocumentWriter':
        """Add tip."""
        self._core.add_tip(content, title)
        return self
    
    def add_warning(self, content: str, title: str = None) -> 'DocumentWriter':
        """Add warning."""
        self._core.add_warning(content, title)
        return self
        
    def add_error(self, content: str, title: str = None) -> 'DocumentWriter':
        """Add error."""
        self._core.add_error(content, title)
        return self
        
    def add_success(self, content: str, title: str = None) -> 'DocumentWriter':
        """Add success."""
        self._core.add_success(content, title)
        return self
        
    def add_caution(self, content: str, title: str = None) -> 'DocumentWriter':
        """Add caution."""
        self._core.add_caution(content, title)
        return self
        
    def add_important(self, content: str, title: str = None) -> 'DocumentWriter':
        """Add important."""
        self._core.add_important(content, title)
        return self
        
    def add_information(self, content: str, title: str = None) -> 'DocumentWriter':
        """Add information."""
        self._core.add_information(content, title)
        return self
        
    def add_recommendation(self, content: str, title: str = None) -> 'DocumentWriter':
        """Add recommendation."""
        self._core.add_recommendation(content, title)
        return self
        
    def add_advice(self, content: str, title: str = None) -> 'DocumentWriter':
        """Add advice."""
        self._core.add_advice(content, title)
        return self
        
    def add_risk(self, content: str, title: str = None) -> 'DocumentWriter':
        """Add risk."""
        self._core.add_risk(content, title)
        return self
    
    def add_chunk(self, code: str, language: str = 'python', **kwargs) -> 'DocumentWriter':
        """Add code chunk."""
        self._core.add_chunk(code, language, **kwargs)
        return self
    
    def add_chunk_executable(self, code: str, language: str = 'python', **kwargs) -> 'DocumentWriter':
        """Add executable code chunk."""
        self._core.add_chunk_executable(code, language, **kwargs)
        return self
        
    def add_plot(self, fig, title: str = None, caption: str = None, source: str = None) -> 'DocumentWriter':
        """Add plot."""
        self._core.add_plot(fig, title, caption, source)
        return self
        
    def add_image(self, path: str, caption: str = None, width: str = None, **kwargs) -> 'DocumentWriter':
        """Add image."""
        self._core.add_image(path, caption, width, **kwargs)
        return self
        
    def add_reference(self, ref_type: str, ref_id: str, custom_text: str = None) -> 'DocumentWriter':
        """Add reference."""
        self._core.add_reference(ref_type, ref_id, custom_text)
        return self
        
    def add_citation(self, citation_key: str, page: str = None) -> 'DocumentWriter':
        """Add citation."""
        self._core.add_citation(citation_key, page)
        return self
        
    def add_markdown_file(self, file_path: str, fix_image_paths: bool = True, 
                         convert_tables: bool = True) -> 'DocumentWriter':
        """Add markdown file."""
        self._core.add_markdown_file(file_path, fix_image_paths, convert_tables)
        return self
    
    def add_quarto_file(self, file_path: str, include_yaml: bool = False, 
                       fix_image_paths: bool = True, convert_tables: bool = True) -> 'DocumentWriter':
        """Add quarto file."""
        self._core.add_quarto_file(file_path, include_yaml, fix_image_paths, convert_tables)
        return self
    
    def generate(self, markdown: bool = False, html: bool = True, pdf: bool = True,
                qmd: bool = True, tex: bool = False, output_filename: str = None) -> Dict[str, Any]:
        """Generate documents."""
        return self._core.generate(markdown, html, pdf, qmd, tex, output_filename)

