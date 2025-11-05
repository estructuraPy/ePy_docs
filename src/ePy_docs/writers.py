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

from typing import List, Dict, Any, Union
import pandas as pd


class DocumentWriter:
    """
    Unified document writer - PURE DELEGATION to core modules.
    
    Usage:
        writer = DocumentWriter("report", layout_style="classic")
        writer = DocumentWriter("paper", layout_style="academic")
        writer = DocumentWriter("report", project_file="custom_project.json")
    """
    
    def __init__(self, document_type: str = "report", layout_style: str = None, project_file: str = None, language: str = None, columns: int = None):
        """Initialize - PURE DELEGATION to core text module.
        
        Args:
            document_type: Type of document - 'paper' (manuscript), 'book', 'report', or 'presentations' (beamer). Default 'report'.
            layout_style: Layout style name. If None, uses default for document type.
            project_file: Path to custom project configuration file (JSON or .epyson).
                         If None, uses default project.epyson from config directory.
                         This file overrides project-specific settings like title, author, etc.
            language: Document language ('en', 'es', 'fr', etc.). If None, uses layout default.
            columns: Number of columns for tables/figures (1, 2, or 3). If None, uses layout default.
        """
        from ePy_docs.core._text import DocumentWriterCore
        self._core = DocumentWriterCore(document_type, layout_style, project_file, language, columns)
    
    def add_content(self, content: str) -> 'DocumentWriter':
        """Add raw content directly to the document buffer.
        
        Appends text/markdown content without any processing or formatting.
        Use this for raw markdown, HTML, or plain text insertion.
        
        Args:
            content: Raw text content to append. Can include markdown syntax,
                    HTML tags, or plain text.
        
        Returns:
            Self for method chaining.
            
        Example:
            writer.add_content("# Custom Header\\n\\nCustom paragraph")
            writer.add_content("<div class='custom'>Custom HTML</div>")
        """
        self._core.add_content(content)
        return self
    
    def get_content(self) -> str:
        """Get the accumulated document content as a single string.
        
        Returns the complete content buffer joined into one string.
        Useful for debugging or previewing document content before generation.
        
        Returns:
            Complete document content as string.
            
        Example:
            content = writer.get_content()
            print(f"Document length: {len(content)} characters")
        """
        return self._core.get_content()
    
    def add_h1(self, text: str) -> 'DocumentWriter':
        """Add H1 (top-level) header.
        
        Args:
            text: Header text.
        
        Returns:
            Self for method chaining.
        """
        self._core.add_h1(text)
        return self
    
    def add_h2(self, text: str) -> 'DocumentWriter':
        """Add H2 (second-level) header.
        
        Args:
            text: Header text.
        
        Returns:
            Self for method chaining.
        """
        self._core.add_h2(text)
        return self
    
    def add_h3(self, text: str) -> 'DocumentWriter':
        """Add H3 (third-level) header.
        
        Args:
            text: Header text.
        
        Returns:
            Self for method chaining.
        """
        self._core.add_h3(text)
        return self
    
    def add_h4(self, text: str) -> 'DocumentWriter':
        """Add H4 (fourth-level) header.
        
        Args:
            text: Header text.
        
        Returns:
            Self for method chaining.
        """
        self._core.add_h4(text)
        return self
    
    def add_h5(self, text: str) -> 'DocumentWriter':
        """Add H5 (fifth-level) header.
        
        Args:
            text: Header text.
        
        Returns:
            Self for method chaining.
        """
        self._core.add_h5(text)
        return self
    
    def add_h6(self, text: str) -> 'DocumentWriter':
        """Add H6 (sixth-level) header.
        
        Args:
            text: Header text.
        
        Returns:
            Self for method chaining.
        """
        self._core.add_h6(text)
        return self
    
    def add_text(self, content: str) -> 'DocumentWriter':
        """Add paragraph text with automatic formatting.
        
        Args:
            content: Paragraph text. Supports inline markdown (bold, italic, etc.).
        
        Returns:
            Self for method chaining.
            
        Example:
            writer.add_text("This is a paragraph with **bold** and *italic* text.")
        """
        self._core.add_text(content)
        return self
    
    def add_list(self, items: List[str], ordered: bool = False) -> 'DocumentWriter':
        """Add list (ordered or unordered).
        
        Args:
            items: List of strings, one per item.
            ordered: If True, creates numbered list. If False (default), creates bullet list.
        
        Returns:
            Self for method chaining.
            
        Example:
            writer.add_list(["First item", "Second item"], ordered=True)
            writer.add_list(["Bullet 1", "Bullet 2"], ordered=False)
        """
        self._core.add_list(items, ordered)
        return self
    
    def add_unordered_list(self, items: List[str]) -> 'DocumentWriter':
        """Add unordered (bullet) list.
        
        Shortcut for add_list(items, ordered=False).
        
        Args:
            items: List of strings, one per item.
        
        Returns:
            Self for method chaining.
        """
        self._core.add_unordered_list(items)
        return self
    
    def add_ordered_list(self, items: List[str]) -> 'DocumentWriter':
        """Add ordered (numbered) list.
        
        Shortcut for add_list(items, ordered=True).
        
        Args:
            items: List of strings, one per item.
        
        Returns:
            Self for method chaining.
        """
        self._core.add_ordered_list(items)
        return self
    
    def add_table(self, df: pd.DataFrame, title: str = None, 
                  show_figure: bool = True, columns: Union[float, List[float], None] = None, **kwargs) -> 'DocumentWriter':
        """Add table with automatic styling based on layout.
        
        Args:
            df: DataFrame containing table data to render.
            title: Table title/caption. If None, auto-generates "Tabla {N}" or "Table {N}".
            show_figure: If True, displays the generated table image immediately in Jupyter notebooks
                        for interactive development. Default True. The table is always included in 
                        the final document regardless of this setting.
            columns: Width specification for multi-column layouts:
                    - None (default): Uses single column width (full page width)
                    - float: Number of columns to span (e.g., 1.0, 1.5, 2.0)
                    - List[float]: Specific widths in inches for different document types
            max_rows_per_table: Maximum rows per table before splitting. Can be:
                               - int: Fixed rows per table part (e.g., 20)
                               - List[int]: Variable rows per part (e.g., [10, 15, 20])
                               - None (default): No splitting, render entire table
            hide_columns: Column name(s) to hide from display. Can be:
                         - str: Single column name (e.g., "ID")
                         - List[str]: Multiple columns (e.g., ["ID", "Internal_Code"])
            filter_by: Dictionary to filter rows before rendering.
                      Format: {"column_name": value} or {"column_name": [value1, value2]}
            sort_by: Column name(s) to sort by before rendering. Can be:
                    - str: Single column (e.g., "Date")
                    - List[str]: Multiple columns (e.g., ["Category", "Date"])
            width_inches: Override width in inches. If specified, ignores columns parameter.
            
        Returns:
            Self for method chaining.
            
        Example:
            writer.add_table(df, title="Project Data", show_figure=True)
            writer.add_table(df, columns=2.0, max_rows_per_table=25)
            writer.add_table(df, hide_columns=["ID"], sort_by="Date")
        """
        self._core.add_table(df, title, show_figure, columns=columns, **kwargs)
        return self
    
    def add_colored_table(self, df: pd.DataFrame, title: str = None, 
                          show_figure: bool = True, columns: Union[float, List[float], None] = None, **kwargs) -> 'DocumentWriter':
        """Add colored table with automatic category detection and column highlighting.
        
        This method creates tables with color gradients applied to specific columns,
        useful for emphasizing numerical data, stress/strain values, or categorical data.
        
        Args:
            df: DataFrame containing table data to render.
            title: Table title/caption. If None, auto-generates "Tabla {N}" or "Table {N}".
            show_figure: If True, displays the generated table image immediately in Jupyter notebooks
                        for interactive development. Default True. The table is always included in 
                        the final document regardless of this setting.
            columns: Width specification for multi-column layouts:
                    - None (default): Uses single column width (full page width)
                    - float: Number of columns to span (e.g., 1.0, 1.5, 2.0)
                    - List[float]: Specific widths in inches for different document types
            highlight_columns: Column name(s) to highlight with color gradient. Can be:
                              - str: Single column name (e.g., "Esfuerzo")
                              - List[str]: Multiple columns (e.g., ["Force", "Moment"])
                              The gradient applies from light (low values) to dark (high values).
            palette_name: Color palette name for highlighting. Available palettes:
                         - Color palettes: 'blues', 'reds', 'greens', 'oranges', 'purples'
                         - Neutral palettes: 'minimal' (pure B&W), 'monochrome' (grays), 'neutrals'
                         - Professional: 'professional', 'scientific', 'technical', 'corporate'
                         - Status: 'status_positive', 'status_negative', 'status_warning', 'status_info'
                         If None, auto-detects based on table category or uses 'blues' as default.
            pallete_name: Alias for palette_name (accepts common typo).
            max_rows_per_table: Maximum rows per table before splitting. Can be:
                               - int: Fixed rows per table part (e.g., 20)
                               - List[int]: Variable rows per part (e.g., [10, 15, 20])
                               - None (default): No splitting, render entire table
            hide_columns: Column name(s) to hide from display. Can be:
                         - str: Single column name (e.g., "ID")
                         - List[str]: Multiple columns (e.g., ["ID", "Internal_Code"])
            filter_by: Dictionary to filter rows before rendering.
                      Format: {"column_name": value} or {"column_name": [value1, value2]}
            sort_by: Column name(s) to sort by before rendering. Can be:
                    - str: Single column (e.g., "Date")
                    - List[str]: Multiple columns (e.g., ["Category", "Date"])
            width_inches: Override width in inches. If specified, ignores columns parameter.
            
        Returns:
            Self for method chaining.
            
        Example:
            # Highlight stress column with red gradient
            writer.add_colored_table(df, title="Stress Analysis", 
                                    palette_name='reds', 
                                    highlight_columns='Esfuerzo')
            
            # Multiple highlighted columns with custom palette
            writer.add_colored_table(df, 
                                    palette_name='blues',
                                    highlight_columns=['Force', 'Moment'])
            
            # With table splitting and filtering
            writer.add_colored_table(df, 
                                    max_rows_per_table=[15, 10],
                                    filter_by={"Type": "Active"},
                                    sort_by="Date")
        """
        self._core.add_colored_table(df, title, show_figure, columns=columns, **kwargs)
        return self
    
    def add_equation(self, latex_code: str, caption: str = None, label: str = None) -> 'DocumentWriter':
        """Add mathematical equation block with LaTeX syntax.
        
        Args:
            latex_code: LaTeX mathematical expression (without delimiters like $ or $$).
                       Example: "E = mc^2" or "\\frac{-b \\pm \\sqrt{b^2-4ac}}{2a}"
            caption: Equation caption/description. Optional.
            label: Reference label for cross-referencing (e.g., "eq-einstein").
                  Used with add_reference() for equation references.
        
        Returns:
            Self for method chaining.
            
        Example:
            writer.add_equation("E = mc^2", caption="Mass-energy equivalence", label="eq-einstein")
            writer.add_equation("\\sum_{i=1}^{n} x_i", caption="Summation")
        """
        self._core.add_equation(latex_code, caption, label)
        return self
    
    def add_inline_equation(self, latex_code: str) -> 'DocumentWriter':
        """Add inline mathematical equation within text flow.
        
        Args:
            latex_code: LaTeX mathematical expression for inline rendering.
                       Example: "x^2 + y^2 = z^2"
        
        Returns:
            Self for method chaining.
            
        Example:
            writer.add_text("The Pythagorean theorem states that ")
            writer.add_inline_equation("a^2 + b^2 = c^2")
            writer.add_text(" for right triangles.")
        """
        self._core.add_inline_equation(latex_code)
        return self
    
    def add_callout(self, content: str, type: str = "note", title: str = None) -> 'DocumentWriter':
        """Add styled callout box for highlighting important information.
        
        Callouts are colored boxes that draw attention to specific content types.
        Available types: note, tip, warning, error, success, caution, important, 
                        information, recommendation, advice, risk.
        
        Args:
            content: Callout text content. Supports markdown formatting.
            type: Callout type that determines styling and color:
                 - "note": General information (blue)
                 - "tip": Helpful suggestions (green)
                 - "warning": Caution/alerts (yellow/orange)
                 - "error": Error messages (red)
                 - "success": Success messages (green)
                 - "caution": Important warnings (orange)
                 - "important": Critical information (purple/red)
                 - "information": Informational content (blue)
                 - "recommendation": Recommended actions (green)
                 - "advice": Advisory content (blue)
                 - "risk": Risk assessment (red)
            title: Callout title. If None, uses default title based on type.
        
        Returns:
            Self for method chaining.
            
        Example:
            writer.add_callout("Always check units before calculations", 
                              type="warning", title="Unit Verification")
            writer.add_callout("This method is deprecated", type="error")
        """
        self._core.add_callout(content, type, title)
        return self
    
    def add_note(self, content: str, title: str = None) -> 'DocumentWriter':
        """Add note callout (blue styling) for general information.
        
        Shortcut for add_callout(content, type="note", title=title).
        
        Args:
            content: Note text content. Supports markdown formatting.
            title: Note title. If None, uses "Note" as default.
        
        Returns:
            Self for method chaining.
        """
        self._core.add_note(content, title)
        return self
    
    def add_tip(self, content: str, title: str = None) -> 'DocumentWriter':
        """Add tip callout (green styling) for helpful suggestions.
        
        Shortcut for add_callout(content, type="tip", title=title).
        
        Args:
            content: Tip text content. Supports markdown formatting.
            title: Tip title. If None, uses "Tip" as default.
        
        Returns:
            Self for method chaining.
        """
        self._core.add_tip(content, title)
        return self
    
    def add_warning(self, content: str, title: str = None) -> 'DocumentWriter':
        """Add warning callout (yellow/orange styling) for cautions.
        
        Shortcut for add_callout(content, type="warning", title=title).
        
        Args:
            content: Warning text content. Supports markdown formatting.
            title: Warning title. If None, uses "Warning" as default.
        
        Returns:
            Self for method chaining.
        """
        self._core.add_warning(content, title)
        return self
        
    def add_error(self, content: str, title: str = None) -> 'DocumentWriter':
        """Add error callout (red styling) for error messages.
        
        Shortcut for add_callout(content, type="error", title=title).
        
        Args:
            content: Error text content. Supports markdown formatting.
            title: Error title. If None, uses "Error" as default.
        
        Returns:
            Self for method chaining.
        """
        self._core.add_error(content, title)
        return self
        
    def add_success(self, content: str, title: str = None) -> 'DocumentWriter':
        """Add success callout (green styling) for success messages.
        
        Shortcut for add_callout(content, type="success", title=title).
        
        Args:
            content: Success text content. Supports markdown formatting.
            title: Success title. If None, uses "Success" as default.
        
        Returns:
            Self for method chaining.
        """
        self._core.add_success(content, title)
        return self
        
    def add_caution(self, content: str, title: str = None) -> 'DocumentWriter':
        """Add caution callout (orange styling) for important warnings.
        
        Shortcut for add_callout(content, type="caution", title=title).
        
        Args:
            content: Caution text content. Supports markdown formatting.
            title: Caution title. If None, uses "Caution" as default.
        
        Returns:
            Self for method chaining.
        """
        self._core.add_caution(content, title)
        return self
        
    def add_important(self, content: str, title: str = None) -> 'DocumentWriter':
        """Add important callout (purple/red styling) for critical information.
        
        Shortcut for add_callout(content, type="important", title=title).
        
        Args:
            content: Important text content. Supports markdown formatting.
            title: Important title. If None, uses "Important" as default.
        
        Returns:
            Self for method chaining.
        """
        self._core.add_important(content, title)
        return self
        
    def add_information(self, content: str, title: str = None) -> 'DocumentWriter':
        """Add information callout (blue styling) for informational content.
        
        Shortcut for add_callout(content, type="information", title=title).
        
        Args:
            content: Information text content. Supports markdown formatting.
            title: Information title. If None, uses "Information" as default.
        
        Returns:
            Self for method chaining.
        """
        self._core.add_information(content, title)
        return self
        
    def add_recommendation(self, content: str, title: str = None) -> 'DocumentWriter':
        """Add recommendation callout (green styling) for recommended actions.
        
        Shortcut for add_callout(content, type="recommendation", title=title).
        
        Args:
            content: Recommendation text content. Supports markdown formatting.
            title: Recommendation title. If None, uses "Recommendation" as default.
        
        Returns:
            Self for method chaining.
        """
        self._core.add_recommendation(content, title)
        return self
        
    def add_advice(self, content: str, title: str = None) -> 'DocumentWriter':
        """Add advice callout (blue styling) for advisory content.
        
        Shortcut for add_callout(content, type="advice", title=title).
        
        Args:
            content: Advice text content. Supports markdown formatting.
            title: Advice title. If None, uses "Advice" as default.
        
        Returns:
            Self for method chaining.
        """
        self._core.add_advice(content, title)
        return self
        
    def add_risk(self, content: str, title: str = None) -> 'DocumentWriter':
        """Add risk callout (red styling) for risk assessment.
        
        Shortcut for add_callout(content, type="risk", title=title).
        
        Args:
            content: Risk text content. Supports markdown formatting.
            title: Risk title. If None, uses "Risk" as default.
        
        Returns:
            Self for method chaining.
        """
        self._core.add_risk(content, title)
        return self
    
    def add_chunk(self, code: str, language: str = 'python', **kwargs) -> 'DocumentWriter':
        """Add code chunk (non-executable code block) for display only.
        
        Args:
            code: Source code to display.
            language: Programming language for syntax highlighting.
                     Common values: 'python', 'r', 'javascript', 'bash', 'sql', 'cpp', 'java'
            eval: If False, code is not executed (default for add_chunk).
            echo: If True, shows code in output (default True).
            output: If False, hides code output (default False for add_chunk).
            
        Returns:
            Self for method chaining.
            
        Example:
            writer.add_chunk("def hello():\\n    print('Hello')", language='python')
            writer.add_chunk("SELECT * FROM users", language='sql')
        """
        self._core.add_chunk(code, language, **kwargs)
        return self
    
    def add_chunk_executable(self, code: str, language: str = 'python', **kwargs) -> 'DocumentWriter':
        """Add executable code chunk that runs during document generation.
        
        Args:
            code: Source code to execute and display.
            language: Programming language for execution.
                     Supported: 'python', 'r' (requires R installation)
            eval: If True, code is executed (default for add_chunk_executable).
            echo: If True, shows code in output (default True).
            output: If True, shows code output (default True for add_chunk_executable).
            
        Returns:
            Self for method chaining.
            
        Example:
            writer.add_chunk_executable("import numpy as np\\nprint(np.pi)")
            writer.add_chunk_executable("x = [1, 2, 3]\\nprint(sum(x))")
        """
        self._core.add_chunk_executable(code, language, **kwargs)
        return self
        
    def add_plot(self, fig, title: str = None, caption: str = None, source: str = None, 
                 columns: Union[float, List[float], None] = None, palette_name: str = None) -> 'DocumentWriter':
        """Add plot.
        
        Args:
            fig: Matplotlib figure object.
            title: Plot title.
            caption: Plot caption.
            source: Source information.
            columns: Width specification for multi-column layouts:
                    - None: Use default width from layout style
                    - float: Number of columns to span (e.g., 1.0, 1.5, 2.0)
                    - List[float]: Specific widths in inches for different document types
            palette_name: Color palette for plot colors (e.g., 'blues', 'reds', 'minimal').
                         If specified, matplotlib will use only colors from this palette.
                         If None, matplotlib uses its default color cycle.
        
        Returns:
            Self for method chaining.
        """
        self._core.add_plot(fig, title, caption, source, columns=columns, palette_name=palette_name)
        return self
        
    def add_image(self, path: str, caption: str = None, width: str = None, 
                  columns: Union[float, List[float], None] = None, **kwargs) -> 'DocumentWriter':
        """Add image from file with automatic path resolution.
        
        Args:
            path: Path to image file. Supports:
                 - Absolute paths: "/path/to/image.png"
                 - Relative paths: "images/figure.png" (relative to document)
                 - Remote URLs: "https://example.com/image.jpg"
                 Supported formats: PNG, JPG, JPEG, SVG, PDF
            caption: Image caption/title. If None, no caption is added.
            width: Image width specification (deprecated, use columns instead).
                  Legacy format: "80%" or "6in"
            columns: Width specification for multi-column layouts:
                    - None (default): Uses default width from layout style or width parameter
                    - float: Number of columns to span (e.g., 1.0, 1.5, 2.0)
                    - List[float]: Specific widths in inches for different document types
            alt_text: Alternative text for accessibility (used in HTML alt attribute).
            responsive: If True (default), image scales responsively in HTML output.
            
        Returns:
            Self for method chaining.
            
        Example:
            writer.add_image("results/plot.png", caption="Stress distribution")
            writer.add_image("logo.svg", columns=0.5)
            writer.add_image("diagram.pdf", alt_text="System diagram", responsive=True)
        """
        self._core.add_image(path, caption, width, columns=columns, **kwargs)
        return self
        
    def add_reference(self, ref_type: str, ref_id: str, custom_text: str = None) -> 'DocumentWriter':
        """Add cross-reference to tables, figures, or equations.
        
        Args:
            ref_type: Type of reference. Options:
                     - "table" or "tbl": References to tables
                     - "figure" or "fig": References to figures/plots
                     - "equation" or "eq": References to equations
            ref_id: Reference identifier (e.g., "tbl-1", "fig-stress", "eq-einstein").
                   Should match the label assigned when creating the element.
            custom_text: Custom reference text. If None, uses auto-generated text
                        (e.g., "Table 1", "Figure 2", "Equation 3").
        
        Returns:
            Self for method chaining.
            
        Example:
            writer.add_reference("table", "tbl-results")
            writer.add_reference("fig", "fig-stress", custom_text="the stress plot")
            writer.add_text("As shown in ")
            writer.add_reference("equation", "eq-1")
        """
        self._core.add_reference(ref_type, ref_id, custom_text)
        return self
        
    def add_citation(self, citation_key: str, page: str = None) -> 'DocumentWriter':
        """Add bibliographic citation from bibliography file.
        
        Requires bibliography file specified in project configuration or passed to generate().
        
        Args:
            citation_key: Citation key from bibliography file (e.g., "Einstein1905").
            page: Specific page number(s) for the citation (e.g., "42" or "15-20").
                 Optional. If provided, formats as "Author (Year, p. 42)".
        
        Returns:
            Self for method chaining.
            
        Example:
            writer.add_citation("Einstein1905")
            writer.add_citation("Smith2020", page="127")
            writer.add_text("According to ")
            writer.add_citation("Johnson2018")
        """
        self._core.add_citation(citation_key, page)
        return self
        
    def add_markdown_file(self, file_path: str, fix_image_paths: bool = True, 
                         convert_tables: bool = True) -> 'DocumentWriter':
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
        self._core.add_markdown_file(file_path, fix_image_paths, convert_tables)
        return self
    
    def add_quarto_file(self, file_path: str, include_yaml: bool = False, 
                       fix_image_paths: bool = True, convert_tables: bool = True) -> 'DocumentWriter':
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
            writer.add_quarto_file("results.qmd", convert_tables=True)
        """
        self._core.add_quarto_file(file_path, include_yaml, fix_image_paths, convert_tables)
        return self
    
    def generate(self, markdown: bool = False, html: bool = True, pdf: bool = True,
                qmd: bool = True, tex: bool = False, output_filename: str = None) -> Dict[str, Any]:
        """Generate output documents in specified formats.
        
        This method finalizes the document and generates files in the requested formats.
        After generation, the writer instance cannot be reused - create a new instance
        for additional documents.
        
        Args:
            markdown: If True, generates standalone Markdown (.md) file.
                     Contains the raw markdown without Quarto-specific features.
                     Default False.
            html: If True (default), generates HTML file via Quarto rendering.
                 Produces a self-contained HTML document with embedded styles and images.
            pdf: If True (default), generates PDF file via Quarto rendering.
                Requires Quarto and a LaTeX distribution (TinyTeX, TeX Live, or MiKTeX).
            qmd: If True (default), generates Quarto (.qmd) source file.
                This is the intermediate format used by Quarto for rendering.
            tex: If True, generates LaTeX (.tex) file.
                Useful for advanced LaTeX customization. Default False.
            output_filename: Base filename for generated files (without extension).
                           If None, uses "Document" as default.
                           Example: "Final_Report" generates "Final_Report.html", "Final_Report.pdf", etc.
        
        Returns:
            Dictionary with paths to generated files:
            {
                'html': '/path/to/document.html',
                'pdf': '/path/to/document.pdf',
                'qmd': '/path/to/document.qmd',
                'markdown': '/path/to/document.md',  # if markdown=True
                'tex': '/path/to/document.tex'  # if tex=True
            }
            
        Raises:
            RuntimeError: If document has already been generated.
            ValueError: If content buffer is empty (no content added).
            
        Note:
            - PDF generation requires Quarto and a LaTeX distribution
            - HTML is self-contained and includes all images and styles
            - After generation, create a new DocumentWriter instance for new documents
            - Generated files are saved to the output directory specified by document_type
            
        Example:
            # Generate only HTML
            result = writer.generate(html=True, pdf=False, qmd=False)
            print(f"HTML file: {result['html']}")
            
            # Generate all formats with custom filename
            result = writer.generate(
                markdown=True, html=True, pdf=True, qmd=True, tex=True,
                output_filename="Engineering_Report_2024"
            )
        """
        return self._core.generate(markdown, html, pdf, qmd, tex, output_filename)

