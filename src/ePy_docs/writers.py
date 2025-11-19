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
        writer = DocumentWriter("paper", layout_style="academic")  
        writer = DocumentWriter("report", project_file="custom_project.json")
        
    Workflow:
        writer.add_h1("Title").add_text("Content").add_table(df).generate()
    """
    
    def __init__(self, document_type: str = "report", layout_style: str = None, project_file: str = None, language: str = None, columns: int = None):
        """Initialize with true inheritance from DocumentWriterCore.
        
        Design: Pure delegation to parent constructor, no additional logic.
        This follows the Liskov Substitution Principle - this class can be used
        anywhere DocumentWriterCore is expected without behavior changes.
        
        Args:
            document_type: Type of document - 'paper' (manuscript), 'book', 'report', or 'presentations' (beamer). Default 'report'.
                          Maps to specific output directories and default configurations.
            layout_style: Layout style name from config/layouts/ directory. If None, uses default for document type.
                         Available: academic, classic, corporate, creative, handwritten, minimal, professional, scientific, technical.
            project_file: Path to custom project configuration file (JSON or .epyson).
                         If None, uses default project.epyson from config directory.
                         This file overrides project-specific settings like title, author, etc.
            language: Document language ('en', 'es', 'fr', etc.). If None, uses layout default.
                     Affects localization of auto-generated text (Figure, Table, etc.).
            columns: Number of columns for tables/figures (1 or 2). If None, uses layout default.
                    Controls default width calculations for responsive layouts.
                    
        Configuration Hierarchy (highest to lowest priority):
        1. Method parameters (add_table, add_image, etc.)
        2. Layout style configuration (layout_style parameter)
        3. Document type defaults
        4. System defaults from epyson files
        """
        # True inheritance - call parent constructor with zero additional overhead
        super().__init__(document_type, layout_style, project_file, language, columns)
    
    def _calculate_width_from_column_span(self, column_span: float, return_inches: bool = False) -> Optional[str]:
        """Calculate width from column span for automatic sizing.
        
        Args:
            column_span: Number of columns to span (e.g., 1.0, 1.5, 2.0)
            return_inches: If True, return width in inches as float, else as string for HTML/CSS
            
        Returns:
            Width specification string (e.g., "80%", "6in") or float if return_inches=True
        """
        if column_span is None:
            return None
            
        try:
            from ePy_docs.core._document import ColumnWidthCalculator
            from ePy_docs.core._config import ModularConfigLoader
            
            # Get document configuration 
            config_loader = ModularConfigLoader()
            doc_config = config_loader.load_external('document_types')
            doc_types = doc_config.get('document_types', {})
            
            if self.document_type not in doc_types:
                return None
                
            type_config = doc_types[self.document_type]
            layout_columns = type_config.get('default_columns', 1)
            
            # Calculate width using ColumnWidthCalculator
            calculator = ColumnWidthCalculator()
            width_inches = calculator.calculate_width(self.document_type, layout_columns, column_span)
            
            if return_inches:
                return width_inches
            
            # Convert to appropriate string format
            if width_inches:
                # For single column layouts or full width, use percentage
                if column_span >= layout_columns:
                    return "100%"
                else:
                    # Calculate percentage based on column span
                    percentage = (column_span / layout_columns) * 100
                    return f"{percentage:.0f}%"
                    
        except Exception:
            # Fallback to simple percentage calculation
            if column_span <= 1:
                return "100%" if return_inches else "100%"
            elif column_span <= 2:
                return "50%" if not return_inches else None
            else:
                return "33%" if not return_inches else None
        
        return None

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
        super().add_content(content)
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
        return super().get_content()
    
    def add_h1(self, text: str) -> 'DocumentWriter':
        """Add H1 (top-level) header.
        
        Args:
            text: Header text.
        
        Returns:
            Self for method chaining.
        """
        super().add_h1(text)
        return self
    
    def add_h2(self, text: str) -> 'DocumentWriter':
        """Add H2 (second-level) header.
        
        Args:
            text: Header text.
        
        Returns:
            Self for method chaining.
        """
        super().add_h2(text)
        return self
    
    def add_h3(self, text: str) -> 'DocumentWriter':
        """Add H3 (third-level) header.
        
        Args:
            text: Header text.
        
        Returns:
            Self for method chaining.
        """
        super().add_h3(text)
        return self
    
    def add_h4(self, text: str) -> 'DocumentWriter':
        """Add H4 (fourth-level) header.
        
        Args:
            text: Header text.
        
        Returns:
            Self for method chaining.
        """
        super().add_h4(text)
        return self
    
    def add_h5(self, text: str) -> 'DocumentWriter':
        """Add H5 (fifth-level) header.
        
        Args:
            text: Header text.
        
        Returns:
            Self for method chaining.
        """
        super().add_h5(text)
        return self
    
    def add_h6(self, text: str) -> 'DocumentWriter':
        """Add H6 (sixth-level) header.
        
        Args:
            text: Header text.
        
        Returns:
            Self for method chaining.
        """
        super().add_h6(text)
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
        super().add_text(content)
        return self
    
    def add_dot_list(self, items: List[str], ordered: bool = False) -> 'DocumentWriter':
        """Add list (ordered or unordered).
        
        Args:
            items: List of strings, one per item.
            ordered: If True, creates numbered list. If False (default), creates bullet list.
        
        Returns:
            Self for method chaining.
            
        Example:
            writer.add_dot_list(["First item", "Second item"], ordered=True)
            writer.add_dot_list(["Bullet 1", "Bullet 2"], ordered=False)
        """
        super().add_list(items, ordered)
        return self
    
    def add_list(self, items: List[str], ordered: bool = False) -> 'DocumentWriter':
        """Add list (ordered or unordered). Alias for add_dot_list for backward compatibility.
        
        Args:
            items: List of strings, one per item.
            ordered: If True, creates numbered list. If False (default), creates bullet list.
        
        Returns:
            Self for method chaining.
        """
        return self.add_dot_list(items, ordered)
    
    def add_numbered_list(self, items: List[str]) -> 'DocumentWriter':
        """Add ordered (numbered) list.
        
        Shortcut for add_dot_list(items, ordered=True).
        
        Args:
            items: List of strings, one per item.
        
        Returns:
            Self for method chaining.
        """
        return self.add_dot_list(items, ordered=True)
    
    def add_table(self, df: pd.DataFrame, title: str = None, 
                  show_figure: bool = False, columns: Union[float, List[float], None] = None,
                  column_span: Union[float, None] = None,
                  max_rows_per_table: Union[int, List[int], None] = None,
                  hide_columns: Union[str, List[str], None] = None,
                  filter_by: Dict[str, Any] = None,
                  sort_by: Union[str, List[str], None] = None,
                  width_inches: float = None) -> 'DocumentWriter':
        """Add table with automatic styling based on layout.
        
        Args:
            df: DataFrame containing table data to render.
            title: Table title/caption. If None, auto-generates "Tabla {N}" or "Table {N}".
            show_figure: If True, displays the generated table image immediately in Jupyter notebooks
                        for interactive development. Default False. The table is always included in 
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
            width_inches: Override width in inches.
            
        Returns:
            Self for method chaining.
            
        Example:
            writer.add_table(df, title="Project Data", show_figure=True)
            writer.add_table(df, max_rows_per_table=25)
            writer.add_table(df, hide_columns=["ID"], sort_by="Date")
        """
        # If column_span is specified but columns is not, use column_span for both
        # This ensures that tables spanning multiple columns are rendered at full width
        if column_span is not None and columns is None:
            final_columns = column_span
        elif columns is not None:
            final_columns = columns
        else:
            final_columns = None
        
        super().add_table(df, title, show_figure, columns=final_columns,
                          column_span=column_span,
                          max_rows_per_table=max_rows_per_table,
                          hide_columns=hide_columns, filter_by=filter_by,
                          sort_by=sort_by, width_inches=width_inches)
        return self
    
    def add_colored_table(self, df: pd.DataFrame, title: str = None, 
                          show_figure: bool = False,
                          highlight_columns: Union[str, List[str], None] = None,
                          palette_name: str = None, columns: Union[float, List[float], None] = None,
                          column_span: Union[float, None] = None,
                          max_rows_per_table: Union[int, List[int], None] = None,
                          hide_columns: Union[str, List[str], None] = None,
                          filter_by: Dict[str, Any] = None,
                          sort_by: Union[str, List[str], None] = None,
                          width_inches: float = None) -> 'DocumentWriter':
        """Add colored table with automatic category detection and column highlighting.
        
        This method creates tables with color gradients applied to specific columns,
        useful for emphasizing numerical data, stress/strain values, or categorical data.
        
        Args:
            df: DataFrame containing table data to render.
            title: Table title/caption. If None, auto-generates "Tabla {N}" or "Table {N}".
            show_figure: If True, displays the generated table image immediately in Jupyter notebooks
                        for interactive development. Default False. The table is always included in 
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
        # If column_span is specified but columns is not, use column_span for both
        # This ensures that tables spanning multiple columns are rendered at full width
        if column_span is not None and columns is None:
            final_columns = column_span
        elif columns is not None:
            final_columns = columns
        else:
            final_columns = None
        
        super().add_colored_table(df, title, show_figure, columns=final_columns,
                                  column_span=column_span,
                                  highlight_columns=highlight_columns, palette_name=palette_name,
                                  max_rows_per_table=max_rows_per_table, hide_columns=hide_columns,
                                  filter_by=filter_by, sort_by=sort_by, width_inches=width_inches)
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
        super().add_equation(latex_code, caption, label)
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
        super().add_inline_equation(latex_code)
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
        return self.add_callout(content, type="note", title=title)
    
    def add_tip(self, content: str, title: str = None) -> 'DocumentWriter':
        """Add tip callout (green styling) for helpful suggestions.
        
        Shortcut for add_callout(content, type="tip", title=title).
        
        Args:
            content: Tip text content. Supports markdown formatting.
            title: Tip title. If None, uses "Tip" as default.
        
        Returns:
            Self for method chaining.
        """
        return self.add_callout(content, type="tip", title=title)
    
    def add_warning(self, content: str, title: str = None) -> 'DocumentWriter':
        """Add warning callout (yellow/orange styling) for cautions.
        
        Shortcut for add_callout(content, type="warning", title=title).
        
        Args:
            content: Warning text content. Supports markdown formatting.
            title: Warning title. If None, uses "Warning" as default.
        
        Returns:
            Self for method chaining.
        """
        return self.add_callout(content, type="warning", title=title)
        
    def add_error(self, content: str, title: str = None) -> 'DocumentWriter':
        """Add error callout (red styling) for error messages.
        
        Shortcut for add_callout(content, type="error", title=title).
        
        Args:
            content: Error text content. Supports markdown formatting.
            title: Error title. If None, uses "Error" as default.
        
        Returns:
            Self for method chaining.
        """
        return self.add_callout(content, type="error", title=title)
        
    def add_success(self, content: str, title: str = None) -> 'DocumentWriter':
        """Add success callout (green styling) for success messages.
        
        Shortcut for add_callout(content, type="success", title=title).
        
        Args:
            content: Success text content. Supports markdown formatting.
            title: Success title. If None, uses "Success" as default.
        
        Returns:
            Self for method chaining.
        """
        return self.add_callout(content, type="success", title=title)
        
    def add_important(self, content: str, title: str = None) -> 'DocumentWriter':
        """Add important callout (purple/red styling) for critical information.
        
        Shortcut for add_callout(content, type="important", title=title).
        
        Args:
            content: Important text content. Supports markdown formatting.
            title: Important title. If None, uses "Important" as default.
        
        Returns:
            Self for method chaining.
        """
        return self.add_callout(content, type="important", title=title)
        
    def add_information(self, content: str, title: str = None) -> 'DocumentWriter':
        """Add information callout (blue styling) for informational content.
        
        Shortcut for add_callout(content, type="information", title=title).
        
        Args:
            content: Information text content. Supports markdown formatting.
            title: Information title. If None, uses "Information" as default.
        
        Returns:
            Self for method chaining.
        """
        return self.add_callout(content, type="information", title=title)
        
    def add_risk(self, content: str, title: str = None) -> 'DocumentWriter':
        """Add risk callout (red styling) for risk assessment.
        
        Shortcut for add_callout(content, type="risk", title=title).
        
        Args:
            content: Risk text content. Supports markdown formatting.
            title: Risk title. If None, uses "Risk" as default.
        
        Returns:
            Self for method chaining.
        """
        return self.add_callout(content, type="risk", title=title)
    
    def add_chunk(self, code: str, language: str = 'python', caption: str = None) -> 'DocumentWriter':
        """Add code chunk (non-executable code block) for display only.
        
        Args:
            code: Source code to display.
            language: Programming language for syntax highlighting.
                     Common values: 'python', 'r', 'javascript', 'bash', 'sql', 'cpp', 'java'
            caption: Optional caption for the code block.
            
        Returns:
            Self for method chaining.
            
        Example:
            writer.add_chunk("def hello():\\n    print('Hello')", language='python')
            writer.add_chunk("SELECT * FROM users", language='sql')
        """
        super().add_chunk(code, language, caption=caption)
        return self
    
    def add_chunk_executable(self, code: str, language: str = 'python', caption: str = None) -> 'DocumentWriter':
        """Add executable code chunk that runs during document generation.
        
        Args:
            code: Source code to execute and display.
            language: Programming language for execution.
                     Supported: 'python', 'r' (requires R installation)
            caption: Optional caption for the code block.
            
        Returns:
            Self for method chaining.
            
        Example:
            writer.add_chunk_executable("import numpy as np\\nprint(np.pi)")
            writer.add_chunk_executable("x = [1, 2, 3]\\nprint(sum(x))")
        """
        super().add_chunk_executable(code, language, caption=caption)
        return self
        
    def add_plot(self, fig, title: str = None, caption: str = None, source: str = None, 
                 palette_name: str = None, column_span: Union[float, None] = None) -> 'DocumentWriter':
        """Add plot.
        
        Args:
            fig: Matplotlib figure object.
            title: Plot title.
            caption: Plot caption.
            source: Source information.
            palette_name: Color palette for plot colors (e.g., 'blues', 'reds', 'minimal').
                         If specified, matplotlib will use only colors from this palette.
            column_span: Number of columns to span (e.g., 1.0, 1.5, 2.0). If specified,
                        automatically adjusts figure size based on document columns.
                         If None, matplotlib uses its default color cycle.
        
        Returns:
            Self for method chaining.
        """
        # Auto-adjust figure size if column_span is specified
        if column_span is not None:
            width_inches = self._calculate_width_from_column_span(column_span, return_inches=True)
            if width_inches:
                # Adjust figure size maintaining aspect ratio
                current_size = fig.get_size_inches()
                aspect_ratio = current_size[1] / current_size[0]
                new_height = width_inches * aspect_ratio
                fig.set_size_inches(width_inches, new_height)
                
        super().add_plot(fig, title, caption, source, palette_name=palette_name, column_span=column_span)
        return self
        
    def add_image(self, path: str, caption: str = None, width: str = None,
                  alt_text: str = None, responsive: bool = True, 
                  column_span: Union[float, None] = None) -> 'DocumentWriter':
        """Add image from file with automatic path resolution.
        
        Args:
            path: Path to image file. Supports:
                 - Absolute paths: "/path/to/image.png"
                 - Relative paths: "images/figure.png" (relative to document)
                 - Remote URLs: "https://example.com/image.jpg"
                 Supported formats: PNG, JPG, JPEG, SVG, PDF
            caption: Image caption/title. If None, no caption is added.
            width: Image width specification: "80%" or "6in". If None and column_span
                  is specified, automatically calculates width based on document columns.
            alt_text: Alternative text for accessibility (used in HTML alt attribute).
            responsive: If True (default), image scales responsively in HTML output.
            column_span: Number of columns to span (e.g., 1.0, 1.5, 2.0). If specified
                        and width is None, automatically calculates appropriate width.
            
        Returns:
            Self for method chaining.
            
        Example:
            writer.add_image("results/plot.png", caption="Stress distribution")
            writer.add_image("logo.svg", width="50%")
            writer.add_image("diagram.pdf", alt_text="System diagram", responsive=True)
        """
        # Auto-calculate width if column_span is specified but width is not
        # For multi-column spanning (column_span >= 2), let core handle width calculation
        # to ensure proper LaTeX figure* generation with \textwidth
        final_width = width
        if width is None and column_span is not None and column_span < 2:
            # Only calculate width for partial column spans (< 2)
            # Full-width (>= 2) is handled by core using LaTeX figure* environments
            final_width = self._calculate_width_from_column_span(column_span)
            
        super().add_image(path, caption, final_width,
                          alt_text=alt_text, responsive=responsive, column_span=column_span)
        return self
        
    def add_reference_to_element(self, ref_type: str, ref_id: str, custom_text: str = None) -> 'DocumentWriter':
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
        super().add_reference(ref_type, ref_id, custom_text)
        return self
        
    def add_reference_citation(self, citation_key: str, page: str = None) -> 'DocumentWriter':
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
        super().add_citation(citation_key, page)
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
        super().add_markdown_file(file_path, fix_image_paths, convert_tables)
        return self
    
    def add_quarto_file(self, file_path: str, include_yaml: bool = False, 
                       fix_image_paths: bool = True, convert_tables: bool = True,
                       execute_code_blocks: bool = True) -> 'DocumentWriter':
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
                               chunks using add_chunk_executable. If False, keeps as regular text.
        
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
        super().add_quarto_file(file_path, include_yaml, fix_image_paths, convert_tables, execute_code_blocks)
        return self
    
    def add_word_file(self, file_path: str, preserve_formatting: bool = True,
                     convert_tables: bool = True, extract_images: bool = False,
                     image_output_dir: str = None, fix_image_paths: bool = True) -> 'DocumentWriter':
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
                             extract_images, image_output_dir, fix_image_paths)
        return self
    
    def cleanup_temporary_images(self) -> int:
        """Manually clean up temporary image files.
        
        Removes temporary matplotlib files and other temporary image files,
        keeping only the properly renamed versions (figure_N.png, table_N.png, etc.).
        
        Returns:
            Number of temporary files removed.
            
        Example:
            writer = DocumentWriter()
            writer.add_plot(fig, title="My Plot")
            removed_count = writer.cleanup_temporary_images()
            print(f"Removed {removed_count} temporary files")
        """
        return super().cleanup_temporary_images()

    def generate(self, markdown: bool = False, html: bool = True, pdf: bool = True,
                qmd: bool = True, tex: bool = False, docx: bool = False, 
                output_filename: str = None, bibliography_path: str = None,
                csl_path: str = None) -> Dict[str, Any]:
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
            docx: If True, generates Microsoft Word (.docx) file via Quarto rendering.
                 Requires Quarto to be installed. Default False.
            output_filename: Base filename for generated files (without extension).
                           If None, uses "Document" as default.
                           Example: "Final_Report" generates "Final_Report.html", "Final_Report.pdf", etc.
            bibliography_path: Path to bibliography file (.bib) for citations.
                             If provided, the file will be automatically copied to the output directory
                             and bibliographic citations with @citation_key syntax will be enabled.
                             Can be an absolute path or relative path.
            csl_path: Path to CSL (Citation Style Language) file for citation formatting.
                     If provided, the file will be automatically copied to the output directory.
                     If None and bibliography_path is provided, uses default style (IEEE).
                     Can be an absolute path or relative path.
        
        Returns:
            Dictionary with paths to generated files:
            {
                'html': '/path/to/document.html',
                'pdf': '/path/to/document.pdf',
                'qmd': '/path/to/document.qmd',
                'markdown': '/path/to/document.md',  # if markdown=True
                'tex': '/path/to/document.tex',  # if tex=True
                'docx': '/path/to/document.docx'  # if docx=True
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
            
            # Generate with bibliography
            result = writer.generate(
                pdf=True, 
                output_filename="Research_Paper",
                bibliography_path="references.bib",
                csl_path="ieee.csl"
            )
            
            # Generate all formats with custom filename
            result = writer.generate(
                markdown=True, html=True, pdf=True, qmd=True, tex=True,
                output_filename="Engineering_Report_2024"
            )
        """
        # Auto-load default bibliography and CSL files if not provided
        from pathlib import Path
        from ePy_docs.core._config import get_loader
        
        if bibliography_path is None:
            # Use default references.bib from package assets
            package_root = Path(__file__).parent
            default_bib = package_root / 'config' / 'assets' / 'bibliography' / 'references.bib'
            if default_bib.exists():
                bibliography_path = str(default_bib)
        
        if csl_path is None and bibliography_path is not None:
            # Use default CSL based on layout config
            package_root = Path(__file__).parent
            loader = get_loader()
            layout = loader.load_layout(self.layout_style)
            csl_style = layout.get('citation_style')
            
            if csl_style:
                default_csl = package_root / 'config' / 'assets' / 'bibliography' / f'{csl_style}.csl'
                if default_csl.exists():
                    csl_path = str(default_csl)
        
        # Direct inheritance - pass bibliography parameters as kwargs
        return super().generate(
            markdown=markdown, 
            html=html, 
            pdf=pdf, 
            qmd=qmd, 
            tex=tex, 
            docx=docx, 
            output_filename=output_filename,
            bibliography_path=bibliography_path,
            csl_path=csl_path
        )

    @staticmethod
    def get_available_document_types() -> Dict[str, str]:
        """Get available document types and their descriptions.
        
        Returns:
            Dictionary with document type names as keys and descriptions as values.
            
        Example:
            types = DocumentWriter.get_available_document_types()
            for type_name, description in types.items():
                print(f"{type_name}: {description}")
        """
        return DocumentWriterCore.get_available_document_types()

    @staticmethod
    def get_available_layouts() -> Dict[str, str]:
        """Get available layout styles and their descriptions.
        
        Returns:
            Dictionary with layout names as keys and descriptions as values.
            
        Example:
            layouts = DocumentWriter.get_available_layouts()
            for layout_name, description in layouts.items():
                print(f"{layout_name}: {description}")
        """
        return DocumentWriterCore.get_available_layouts()

    @staticmethod
    def get_available_palettes() -> Dict[str, str]:
        """Get available color palettes and their descriptions.
        
        Returns:
            Dictionary with palette names as keys and descriptions as values.
            
        Example:
            palettes = DocumentWriter.get_available_palettes()
            for palette_name, description in palettes.items():
                print(f"{palette_name}: {description}")
        """
        return DocumentWriterCore.get_available_palettes()

