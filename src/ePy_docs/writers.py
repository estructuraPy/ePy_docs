"""
Unified Document Writers API - TRUE INHERITANCE

This API provides a clean interface that inherits directly from DocumentWriterCore.
All methods have explicit parameter signatures instead of **kwargs for better type safety.

Architecture:
- DocumentWriter: True inheritance from DocumentWriterCore (Liskov Substitution Principle)
- Explicit parameters for all known arguments (Interface Segregation)
- Method chaining preserved for fluent API design
- Single Responsibility: Only handles API layer, delegates logic to core
- Open/Closed: Extensible without modifying existing code
- Dependency Inversion: Depends on DocumentWriterCore abstraction

Design Patterns:
- Wrapper Pattern: Clean delegation to core functionality
- Fluent Interface: Method chaining for natural document building workflow
- Template Method: Core handles the complex logic, this layer provides clean interface

Performance Characteristics:
- Minimal overhead: Only delegation + return self
- Memory efficient: No data duplication, direct inheritance
- Type safe: Explicit signatures prevent runtime errors
"""

from typing import List, Dict, Any, Union, Optional
import pandas as pd
from ePy_docs.core._text import DocumentWriterCore


class DocumentWriter(DocumentWriterCore):
    """
    Unified document writer - True inheritance from DocumentWriterCore.
    
    This class follows SOLID principles:
    - Single Responsibility: API layer only, no business logic
    - Open/Closed: Extensible via configuration, not code modification
    - Liskov Substitution: Perfect subtype of DocumentWriterCore
    - Interface Segregation: Clean, focused API for document generation
    - Dependency Inversion: Depends on abstraction, not concrete implementation
    
    Features:
    - Multi-format output: HTML, PDF, LaTeX, Word, Markdown
    - Engineering-focused: Tables, equations, technical diagrams
    - Configuration-driven: Uses epyson files for layouts and styling
    - Method chaining: Fluent API for natural document construction
    - Type safety: Explicit parameters with comprehensive type hints
    
    Usage:
        writer = DocumentWriter("report", layout_style="classic")
        writer.set_author("Juan Pérez", "Investigador Principal")
        writer.set_project_info("MI-2024-001", "Análisis de Datos")
        writer = DocumentWriter("paper", layout_style="academic")
        writer = DocumentWriter("report", language="es")
        
    Workflow:
        writer.add_h1("Title").add_text("Content").add_table(df).generate()
    """
    
    def __init__(self, document_type: str = "report", layout_style: str = None, language: str = None):
        """Initialize with true inheritance from DocumentWriterCore.
        
        Design: Pure delegation to parent constructor, no additional logic.
        This follows the Liskov Substitution Principle - this class can be used
        anywhere DocumentWriterCore is expected without behavior changes.
        
        Args:
            document_type: Type of document - 'paper' (manuscript), 'book', 'report', or 'notebook'. Default 'report'.
                          Maps to specific output directories and default configurations.
            layout_style: Layout style name from config/layouts/ directory. If None, uses default for document type.
                         Available: academic, classic, corporate, creative, handwritten, minimal, professional, scientific, technical.
            language: Document language ('en', 'es', 'fr', etc.). If None, uses layout default.
                     Affects localization of auto-generated text (Figure, Table, etc.).
                    
        Configuration Hierarchy (highest to lowest priority):
        1. Method parameters (add_table, add_image, etc.)
        2. Layout style configuration (layout_style parameter)
        3. Document type defaults
        4. System defaults from epyson files
        """
        # True inheritance - call parent constructor with zero additional overhead
        super().__init__(document_type, layout_style, language)

    def add_project_info(self, info_type: str = "project", show_list: bool = True) -> 'DocumentWriter':
        """Add project information as unordered list from project configuration.
        
        Args:
            info_type: Type of information ("project", "client", "authors").
            show_list: Whether to display the information as a list.
        
        Returns:
            Self for method chaining.
        """
        super().add_project_info(info_type, show_list)
        return self
    
    def set_author(self, name: str, role: str = None, affiliation: str = None, 
                   contact: str = None) -> 'DocumentWriter':
        """Set document author information.
        
        Args:
            name: Author's full name
            role: Author's role or position (optional)
            affiliation: Author's institution or organization (optional)
            contact: Author's email or contact information (optional)
            
        Returns:
            Self for method chaining.
        """
        super().set_author(name, role, affiliation, contact)
        return self
    
    def set_project_info(self, code: str = None, name: str = None, 
                        project_type: str = None, status: str = None,
                        description: str = None, created_date: str = None,
                        location: str = None) -> 'DocumentWriter':
        """Set project information.
        
        Args:
            code: Project code or identifier
            name: Project name
            project_type: Type of project (e.g., "Research", "Analysis")
            status: Project status (e.g., "Active", "Completed")
            description: Project description
            created_date: Project creation date
            location: Project location
            
        Returns:
            Self for method chaining.
        """
        super().set_project_info(code, name, project_type, status, description, created_date, location)
        return self
    
    def set_client_info(self, name: str = None, company: str = None,
                       contact: str = None, address: str = None) -> 'DocumentWriter':
        """Set client information.
        
        Args:
            name: Client name
            company: Client company
            contact: Client contact information
            address: Client address
            
        Returns:
            Self for method chaining.
        """
        super().set_client_info(name, company, contact, address)
        return self

    def add_content(self, content: str) -> 'DocumentWriter':
        """Add raw content directly to the document buffer.
        
        Args:
            content: Raw text content to append. Can include markdown syntax,
                    HTML tags, or plain text.
        
        Returns:
            Self for method chaining.
        """
        super().add_content(content)
        return self
    
    def add_code_chunk(self, code: str, language: str = "python", chunk_type: str = "display", caption: str = None) -> 'DocumentWriter':
        """Add a code chunk with visual differentiation.
        
        Args:
            code: Source code content
            language: Programming language identifier (default: "python")
            chunk_type: Type of chunk - "display" (light background) or "executable" (colored background)
            caption: Optional caption for the code chunk
        
        Returns:
            Self for method chaining.
        """
        super().add_code_chunk(code, language, chunk_type, caption)
        return self
    
    def add_inline_code_chunk(self, code: str, language: str = "python") -> 'DocumentWriter':
        """Add inline executable code chunk that Quarto evaluates during rendering.
        
        Args:
            code: Code expression to execute inline. Must be a valid expression that returns a value.
            language: Programming language identifier (default: "python").
        
        Returns:
            Self for method chaining.
        """
        super().add_inline_code_chunk(code, language)
        return self
    
    def add_h1(self, text: str) -> 'DocumentWriter':
        """Add H1 (top-level) header."""
        super().add_h1(text)
        return self
    
    def add_h2(self, text: str) -> 'DocumentWriter':
        """Add H2 (second-level) header."""
        super().add_h2(text)
        return self
    
    def add_h3(self, text: str) -> 'DocumentWriter':
        """Add H3 (third-level) header."""
        super().add_h3(text)
        return self
    
    def add_h4(self, text: str) -> 'DocumentWriter':
        """Add H4 (fourth-level) header."""
        super().add_h4(text)
        return self
    
    def add_h5(self, text: str) -> 'DocumentWriter':
        """Add H5 (fifth-level) header."""
        super().add_h5(text)
        return self
    
    def add_h6(self, text: str) -> 'DocumentWriter':
        """Add H6 (sixth-level) header."""
        super().add_h6(text)
        return self
    
    def add_text(self, content: str) -> 'DocumentWriter':
        """Add paragraph text with automatic formatting.
        
        Args:
            content: Paragraph text. Supports inline markdown (bold, italic, etc.).
        
        Returns:
            Self for method chaining.
        """
        super().add_text(content)
        return self
    
    def add_list(self, items, list_type: str = 'bullets') -> 'DocumentWriter':
        """Add list (bullets, numbered, or checklist). Auto-formats dictionaries with sublists.
        
        Args:
            items: List of strings, or dict where values can be scalars or lists.
            list_type: Type of list - 'bullets', 'numbered', or 'checklist' (default: 'bullets')
        
        Returns:
            Self for method chaining.
        """
        super().add_list(items, list_type=list_type)
        return self
    
    def add_numbered_list(self, items: List[str]) -> 'DocumentWriter':
        """Add ordered (numbered) list.
        
        Shortcut for add_list(items, list_type='numbered').
        
        Args:
            items: List of strings, one per item.
        
        Returns:
            Self for method chaining.
        """
        return self.add_list(items, list_type='numbered')
    
    def add_checklist(self, items: List[str]) -> 'DocumentWriter':
        """Add checklist (unchecked tasks).
        
        Creates a list with checkboxes for task tracking.
        
        Args:
            items: List of task strings, one per item.
        
        Returns:
            Self for method chaining.
        """
        super().add_checklist(items)
        return self
    
    def add_table(self, df: pd.DataFrame, title: str = None, 
                  show_figure: bool = False,
                  max_rows_per_table: Union[int, List[int], None] = None,
                  hide_columns: Union[str, List[str], None] = None,
                  filter_by: Dict[str, Any] = None,
                  sort_by: Union[str, List[str], None] = None,
                  width_inches: float = None,
                  label: str = None) -> 'DocumentWriter':
        """Add table with automatic styling based on layout.
        
        Args:
            df: DataFrame containing table data to render.
            title: Table title/caption.
            show_figure: If True, displays the generated table image immediately in Jupyter.
            max_rows_per_table: Maximum rows per table before splitting.
            hide_columns: Column name(s) to hide from display.
            filter_by: Dictionary to filter rows before rendering.
            sort_by: Column name(s) to sort by before rendering.
            width_inches: Override width in inches.
            label: Optional Quarto label for cross-referencing.
            
        Returns:
            Self for method chaining.
        """
        super().add_table(df, title, show_figure,
                          max_rows_per_table=max_rows_per_table,
                          hide_columns=hide_columns, filter_by=filter_by,
                          sort_by=sort_by, width_inches=width_inches, label=label)
        return self
    
    def add_colored_table(self, df: pd.DataFrame, title: str = None, 
                          show_figure: bool = False,
                          highlight_columns: Union[str, List[str], None] = None,
                          palette_name: str = None,
                          max_rows_per_table: Union[int, List[int], None] = None,
                          hide_columns: Union[str, List[str], None] = None,
                          filter_by: Dict[str, Any] = None,
                          sort_by: Union[str, List[str], None] = None,
                          width_inches: float = None,
                          label: str = None) -> 'DocumentWriter':
        """Add colored table with automatic category detection and column highlighting.
        
        Args:
            df: DataFrame containing table data to render.
            title: Table title/caption.
            show_figure: If True, displays the generated table image immediately in Jupyter.
            highlight_columns: Column name(s) to highlight with color gradient.
            palette_name: Color palette name for highlighting.
            max_rows_per_table: Maximum rows per table before splitting.
            hide_columns: Column name(s) to hide from display.
            filter_by: Dictionary to filter rows before rendering.
            sort_by: Column name(s) to sort by before rendering.
            width_inches: Override width in inches.
            label: Optional Quarto label for cross-referencing.
            
        Returns:
            Self for method chaining.
        """
        super().add_colored_table(df, title, show_figure,
                                  highlight_columns=highlight_columns, palette_name=palette_name,
                                  max_rows_per_table=max_rows_per_table, hide_columns=hide_columns,
                                  filter_by=filter_by, sort_by=sort_by, width_inches=width_inches, label=label)
        return self
    
    def add_equation(self, latex_code: str, caption: str = None, label: str = None) -> 'DocumentWriter':
        """Add mathematical equation block with LaTeX syntax.
        
        Args:
            latex_code: LaTeX mathematical expression (without delimiters).
            caption: Equation caption/description.
            label: Reference label for cross-referencing.
        
        Returns:
            Self for method chaining.
        """
        super().add_equation(latex_code, caption, label)
        return self
    
    def add_inline_equation(self, latex_code: str) -> 'DocumentWriter':
        """Add inline mathematical equation within text flow.
        
        Args:
            latex_code: LaTeX mathematical expression for inline rendering.
        
        Returns:
            Self for method chaining.
        """
        super().add_inline_equation(latex_code)
        return self
    
    def add_note(self, content: str, title: str = None) -> 'DocumentWriter':
        """Add note callout (blue styling)."""
        return self.add_callout(content, type="note", title=title)
    
    def add_tip(self, content: str, title: str = None) -> 'DocumentWriter':
        """Add tip callout (green styling)."""
        return self.add_callout(content, type="tip", title=title)
    
    def add_warning(self, content: str, title: str = None) -> 'DocumentWriter':
        """Add warning callout (yellow/orange styling)."""
        return self.add_callout(content, type="warning", title=title)
        
    def add_caution(self, content: str, title: str = None) -> 'DocumentWriter':
        """Add caution callout (orange styling)."""
        return self.add_callout(content, type="caution", title=title)
        
    def add_important(self, content: str, title: str = None) -> 'DocumentWriter':
        """Add important callout (red/pink styling)."""
        return self.add_callout(content, type="important", title=title)
        
    def add_plot(self, fig, title: str = None, caption: str = None, source: str = None, 
                 palette_name: str = None, show_figure: bool = False, label: str = None) -> 'DocumentWriter':
        """Add plot.
        
        Args:
            fig: Matplotlib figure object.
            title: Plot title.
            caption: Plot caption.
            source: Source information.
            palette_name: Color palette for plot colors.
            show_figure: If True, displays the generated plot image immediately in Jupyter.
            label: Optional Quarto label for cross-referencing.
        
        Returns:
            Self for method chaining.
        """
        super().add_plot(fig, title, caption, source, palette_name=palette_name, show_figure=show_figure, label=label)
        return self
        
    def add_image(self, path: str, caption: str = None, width: str = None,
                  alt_text: str = None, responsive: bool = True, label: str = None) -> 'DocumentWriter':
        """Add image from file with automatic path resolution.
        
        Args:
            path: Path to image file (absolute, relative, or URL).
            caption: Image caption/title.
            width: Image width specification.
            alt_text: Alternative text for accessibility.
            responsive: If True (default), image scales responsively.
            label: Optional Quarto label for cross-referencing.
            
        Returns:
            Self for method chaining.
        """
        super().add_image(path, caption, width,
                          alt_text=alt_text, responsive=responsive, label=label)
        return self
        
    def add_reference_to_element(self, ref_type: str, label: str, custom_text: str = None) -> 'DocumentWriter':
        """Add cross-reference to tables, figures, or equations.
        
        Args:
            ref_type: Type of reference ("table", "figure", "equation").
            label: Reference label identifier.
            custom_text: Custom reference text.
        
        Returns:
            Self for method chaining.
        """
        super().add_reference(ref_type, label, custom_text)
        return self
        
    def add_reference_citation(self, citation_key: str, page: str = None) -> 'DocumentWriter':
        """Add bibliographic citation from bibliography file.
        
        Args:
            citation_key: Citation key from bibliography file.
            page: Specific page number(s).
        
        Returns:
            Self for method chaining.
        """
        super().add_citation(citation_key, page)
        return self
    
    def add_page_header(self, content: str) -> 'DocumentWriter':
        """Add page header content for PDF output.
        
        Creates a header that will appear at the top of pages in PDF documents.
        The header automatically uses the color defined in the layout's 
        palette.page.header_color configuration.
        
        Args:
            content: Text content for the header. Supports markdown formatting
                    like **bold**, *italic*, etc. Can include project name,
                    document title, or any custom text.
        
        Returns:
            Self for method chaining.
            
        Note:
            - Header color is automatically taken from layout configuration
            - For PDF output: rendered in document header area
            - For HTML output: appears as regular content at document top
            - Best practice: Call early in document, typically after set_project_info
            
        Example:
            # Simple text header
            writer.add_page_header("Engineering Analysis Report")
            
            # Formatted header
            writer.add_page_header("**Project XYZ** - Structural Analysis")
            
            # With project information
            writer.set_project_info("PROJ-001", "Bridge Design")
            writer.add_page_header("Project PROJ-001: Bridge Design")
        """
        super().add_page_header(content)
        return self
    
    def add_page_footer(self, content: str) -> 'DocumentWriter':
        """Add page footer content for PDF output.
        
        Creates a footer that will appear at the bottom of pages in PDF documents.
        The footer automatically uses the color defined in the layout's
        palette.page.footer_color configuration.
        
        Args:
            content: Text content for the footer. Supports markdown formatting
                    like **bold**, *italic*, etc. Can include copyright,
                    confidentiality notices, or page numbers.
        
        Returns:
            Self for method chaining.
            
        Note:
            - Footer color is automatically taken from layout configuration
            - For PDF output: rendered in document footer area
            - For HTML output: appears as regular content at document bottom
            - Best practice: Call early in document, typically after set_project_info
            
        Example:
            # Simple footer
            writer.add_page_footer("© 2024 Engineering Corp.")
            
            # Confidentiality notice
            writer.add_page_footer("**CONFIDENTIAL** - Internal Use Only")
            
            # Multiple elements
            writer.add_page_footer("© 2024 Company Name | Confidential")
        """
        super().add_page_footer(content)
        return self
        
    def add_markdown_file(self, file_path: str, fix_image_paths: bool = True, 
                         convert_tables: bool = True, show_figure: bool = False) -> 'DocumentWriter':
        """Import and append content from an existing Markdown (.md) file.
        
        The imported content is automatically separated from existing content with spacers
        to prevent markdown rendering issues. Useful for modular document composition.
        
        Args:
            file_path: Path to Markdown file (.md). Can be:
                      - Absolute path: "/full/path/to/document.md"
                      - Relative path: "sections/introduction.md" (relative to current directory)
            fix_image_paths: If True (default), automatically adjusts image paths in the imported
                            markdown to work correctly in the generated document context.
            convert_tables: If True (default), converts markdown tables to styled image tables
                           matching the document layout. If False, keeps original markdown tables.
            show_figure: If True, displays generated table/image content immediately in Jupyter notebooks
                        for interactive development. Default False.
        
        Returns:
            Self for method chaining.
            
        Note:
            Spacers are automatically added before and after the imported content to ensure
            proper markdown rendering and prevent formatting issues with adjacent content.
            
        Example:
            writer.add_h1("Main Document")
            writer.add_markdown_file("sections/intro.md")
            writer.add_markdown_file("sections/methods.md", convert_tables=False)
        """
        super().add_markdown_file(file_path, fix_image_paths, convert_tables, show_figure)
        return self
    

    
    def add_quarto_file(self, file_path: str, include_yaml: bool = False, 
                       fix_image_paths: bool = True, convert_tables: bool = True,
                       execute_code_blocks: bool = True, show_figure: bool = False) -> 'DocumentWriter':
        """Import and append content from an existing Quarto (.qmd) file.
        
        The imported content is automatically separated from existing content with spacers
        to prevent markdown rendering issues. Useful for modular document composition.
        
        Args:
            file_path: Path to Quarto file (.qmd). Can be:
                      - Absolute path: "/full/path/to/document.qmd"
                      - Relative path: "sections/analysis.qmd" (relative to current directory)
            include_yaml: If True, includes the YAML frontmatter from the .qmd file.
                         If False (default), strips YAML and only imports content.
                         Usually False when combining multiple files into one document.
            fix_image_paths: If True (default), automatically adjusts image paths in the imported
                            content to work correctly in the generated document context.
            convert_tables: If True (default), converts markdown tables to styled image tables
                           matching the document layout. If False, keeps original markdown tables.
            execute_code_blocks: If True (default), automatically detects Quarto code blocks
                               (```{python}, ```{r}, etc.) and converts them to executable
                               chunks using add_code_chunk(chunk_type='executable'). If False, keeps as regular text.
            show_figure: If True, displays generated table/image content immediately in Jupyter notebooks
                        for interactive development. Default False.
        
        Returns:
            Self for method chaining.
            
        Note:
            Spacers are automatically added before and after the imported content to ensure
            proper markdown rendering and prevent formatting issues with adjacent content.
            YAML frontmatter is typically excluded (include_yaml=False) when combining
            multiple .qmd files into a single document.
            
        Example:
            writer.add_h1("Complete Analysis")
            writer.add_quarto_file("intro.qmd", include_yaml=False)
            writer.add_quarto_file("results.qmd", convert_tables=True, execute_code_blocks=True)
        """
        super().add_quarto_file(file_path, include_yaml, fix_image_paths, convert_tables, execute_code_blocks, show_figure)
        return self
    
    def add_word_file(self, file_path: str, preserve_formatting: bool = True,
                     convert_tables: bool = True, extract_images: bool = True,
                     image_output_dir: str = None, fix_image_paths: bool = True,
                     show_figure: bool = False) -> 'DocumentWriter':
        """Import and append content from a Word document (.docx) file.
        
        Converts Word document content to Markdown format and integrates it into the current
        document workflow. Supports formatting preservation, table conversion, and image extraction.
        
        Args:
            file_path: Path to Word document (.docx). Can be:
                      - Absolute path: "/full/path/to/document.docx"
                      - Relative path: "sections/report.docx" (relative to current directory)
            preserve_formatting: If True (default), preserves basic text formatting like
                                bold, italic, and strikethrough in the converted content.
            convert_tables: If True (default), converts Word tables to styled image tables
                           matching the document layout. If False, converts to simple Markdown tables.
            extract_images: If True, extracts embedded images from the Word document.
                           Requires image_output_dir to be specified.
            image_output_dir: Directory to save extracted images. Required if extract_images=True.
                             Images will be saved with auto-generated names.
            fix_image_paths: If True (default), adjusts image paths in the imported content
                            to work correctly in the generated document context.
            show_figure: If True, displays generated table/image content immediately in Jupyter notebooks
                        for interactive development. Default False.
        
        Returns:
            Self for method chaining.
            
        Raises:
            ImportError: If python-docx library is not installed.
            FileNotFoundError: If the specified Word document doesn't exist.
            ValueError: If extract_images=True but image_output_dir is not provided.
            
        Note:
            - Requires python-docx library: `pip install python-docx`
            - Content is automatically separated with spacers to prevent formatting issues
            - Headings are converted to Markdown format (H1, H2, etc.)
            - Lists and other formatting elements are preserved where possible
            - Tables can be converted to either image format or simple Markdown
            
        Example:
            # Basic import with formatting preservation
            writer.add_h1("Imported Content")
            writer.add_word_file("report.docx")
            
            # Import with image extraction
            writer.add_word_file("document.docx", 
                               extract_images=True,
                               image_output_dir="extracted_images")
            
            # Import with simple table conversion
            writer.add_word_file("data.docx", convert_tables=False)
        """
        super().add_word_file(file_path, preserve_formatting, convert_tables, 
                             extract_images, image_output_dir, fix_image_paths, show_figure)
        return self

    def generate(self, markdown: bool = False, html: bool = True, pdf: bool = True,
                qmd: bool = True, tex: bool = False, docx: bool = False, 
                output_filename: str = None, bibliography_path: str = None,
                csl_path: str = None) -> Dict[str, Any]:
        """Generate output documents in specified formats.
        
        Args:
            markdown, html, pdf, qmd, tex, docx: Boolean flags for output formats.
            output_filename: Custom filename (without extension).
            bibliography_path: Path to .bib file.
            csl_path: Path to .csl style file.
            
        Returns:
            Dictionary mapping format names to generated file paths.
        """
        return super().generate(
            markdown=markdown, html=html, pdf=pdf, qmd=qmd, tex=tex, docx=docx,
            output_filename=output_filename, bibliography_path=bibliography_path, csl_path=csl_path
        )
        

    @staticmethod
    def get_available_layouts() -> Dict[str, str]:
        """Get available layout styles and their descriptions."""
        return DocumentWriterCore.get_available_layouts()

    @staticmethod
    def get_available_palettes() -> Dict[str, str]:
        """Get available color palettes and their descriptions."""
        return DocumentWriterCore.get_available_palettes()
    
    def reset(self) -> 'DocumentWriter':
        """Reset the document to allow creating new content after generation.
        
        Clears all content, resets counters, and clears project information.
        
        Returns:
            Self for method chaining.
        """
        super().reset_document()
        return self

