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
        
        Automatically generates formatted unordered lists with project-related information.
        Each item uses bold for field names and regular text for values.
        Empty fields are automatically omitted from all lists.
        Lists support internationalization (English and Spanish).
        
        Args:
            info_type: Type of information to display. Options:
                      - "project": Project details (code, name, type, status, description, date, location)
                      - "client": Client information (name, company, contact, address)
                      - "authors": Document authors (names, roles, affiliations, contacts)
            show_list: Whether to display the information as a list. If False, the information
                       is still configured for metadata but no list is generated.
        
        Returns:
            Self for method chaining.
            
        Example:
            writer.add_project_info("project")                    # Project information list
            writer.add_project_info("client")                     # Client information list
            writer.add_project_info("authors")                    # Authors list
            writer.add_project_info("authors", show_list=False)   # Configure authors for metadata only
            
        Output format (project/client):
            ## Project Information
            - **Project Code**: PROJ-001
            - **Project Name**: Bridge Analysis
            - **Status**: Active
            
        Output format (authors):
            ## Authors
            - **Name**: Juan Pérez | **Role**: Lead Engineer | **Affiliation**: University
            - **Name**: María García | **Role**: Researcher
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
            
        Example:
            writer.set_author("Juan Pérez", "Investigador Principal", 
                            "Universidad Nacional", "juan.perez@email.com")
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
            
        Example:
            writer.set_project_info("MI-2024-001", "Análisis de Datos", 
                                  "Research", "Active", "2024-11-21")
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
    
    def add_code_chunk(self, code: str, language: str = "python", chunk_type: str = "display", caption: str = None) -> 'DocumentWriter':
        """Add a code chunk with visual differentiation.
        
        Args:
            code: Source code content
            language: Programming language identifier (default: "python")
            chunk_type: Type of chunk - "display" (light background) or "executable" (colored background)
            caption: Optional caption for the code chunk
        
        Returns:
            Self for method chaining.
            
        Example:
            writer.add_code_chunk('print("hello")', "python", "display", "Example code")
            writer.add_code_chunk('result = calculate()', "python", "executable")
        """
        super().add_code_chunk(code, language, chunk_type, caption)
        return self
    
    def add_inline_code_chunk(self, code: str, language: str = "python") -> 'DocumentWriter':
        """Add inline executable code chunk that Quarto evaluates during rendering.
        
        This method inserts executable code inline within text flow. The code is evaluated
        by Quarto when rendering the document, and its output replaces the code expression.
        Perfect for dynamic values, calculations, or variables that should be computed at
        render time.
        
        Args:
            code: Code expression to execute inline. Must be a valid expression that returns
                 a value. Examples:
                 - Arithmetic: "2 + 2", "sum([1, 2, 3])"
                 - Variables: "result_value", "total_cost"
                 - Functions: "calculate_mean(data)", "get_status()"
                 - Formatted: "f'{percentage:.1f}%'", "round(value, 2)"
            language: Programming language identifier (default: "python").
                     Supported languages: python, r, julia, javascript, bash, etc.
                     Must match a Quarto-supported language.
        
        Returns:
            Self for method chaining.
            
        Important:
            - Code is executed during Quarto rendering, not when calling this method
            - Variables referenced must exist in the document's execution context
            - Code must return a value (not None) to display
            - For code blocks (non-inline), use add_code_chunk() instead
            - For non-executable inline code, use markdown backticks: `code`
            
        Example:
            # Basic calculation inline
            writer.add_text("The result is ")
            writer.add_inline_code_chunk("2 + 2")
            writer.add_text(" units.")
            # Renders as: "The result is 4 units."
            
            # Reference Python variables
            writer.add_code_chunk("total = 100", "python", "executable")
            writer.add_text("Total cost: $")
            writer.add_inline_code_chunk("total")
            # Renders as: "Total cost: $100"
            
            # Formatted output
            writer.add_code_chunk("percentage = 0.847", "python", "executable")
            writer.add_text("Success rate: ")
            writer.add_inline_code_chunk("f'{percentage*100:.1f}%'")
            # Renders as: "Success rate: 84.7%"
            
            # R language inline code
            writer.add_inline_code_chunk("mean(dataset$values)", language="r")
            # Evaluates R expression and displays result
            
            # Multiple inline chunks in sentence
            writer.add_text("The mean is ")
            writer.add_inline_code_chunk("mean(data)")
            writer.add_text(" and the median is ")
            writer.add_inline_code_chunk("median(data)")
            writer.add_text(".")
        """
        super().add_inline_code_chunk(code, language)
        return self
    
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
    
    def add_list(self, items, ordered: bool = False) -> 'DocumentWriter':
        """Add list (ordered or unordered). Auto-formats dictionaries with sublists.
        
        Args:
            items: List of strings, or dict where values can be scalars or lists.
                   Dicts are formatted as "**Key**: value" or "**Key**" with sub-items.
            ordered: If True, creates numbered list. If False (default), creates bullet list.
        
        Returns:
            Self for method chaining.
            
        Example:
            writer.add_list(["First item", "Second item"], ordered=True)
            writer.add_list({"Category": "value", "Units": ["m", "kg"]}, ordered=False)
        """
        super().add_list(items, ordered)
        return self
    
    def add_numbered_list(self, items: List[str]) -> 'DocumentWriter':
        """Add ordered (numbered) list.
        
        Shortcut for add_list(items, ordered=True).
        
        Args:
            items: List of strings, one per item.
        
        Returns:
            Self for method chaining.
        """
        return self.add_list(items, ordered=True)
    
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
            title: Table title/caption. If None, auto-generates "Tabla {N}" or "Table {N}".
            show_figure: If True, displays the generated table image immediately in Jupyter notebooks
                        for interactive development. Default False. The table is always included in 
                        the final document regardless of this setting.
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
            label: Optional Quarto label for cross-referencing (e.g., 'results').
                  When provided, enables references like @tbl-results in text.
                  Without this, the table gets auto-generated ID like tbl-1.
                  For split tables, appends part number (e.g., tbl-results-1, tbl-results-2).
            
        Returns:
            Self for method chaining.
            
        Example:
            writer.add_table(df, title="Project Data", show_figure=True)
            writer.add_table(df, max_rows_per_table=25)
            writer.add_table(df, hide_columns=["ID"], sort_by="Date")
            writer.add_table(df, title="Results", label="results")
            writer.add_text("As shown in @tbl-results...")
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
        
        This method creates tables with color gradients applied to specific columns,
        useful for emphasizing numerical data, stress/strain values, or categorical data.
        
        Args:
            df: DataFrame containing table data to render.
            title: Table title/caption. If None, auto-generates "Tabla {N}" or "Table {N}".
            show_figure: If True, displays the generated table image immediately in Jupyter notebooks
                        for interactive development. Default False. The table is always included in 
                        the final document regardless of this setting.
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
            label: Optional Quarto label for cross-referencing (e.g., 'stress-analysis').
                  When provided, enables references like @tbl-stress-analysis in text.
                  Without this, the table gets auto-generated ID like tbl-1.
                  For split tables, appends part number (e.g., tbl-stress-1, tbl-stress-2).
            
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
            
            # With custom label for cross-referencing
            writer.add_colored_table(df, title="Stress Analysis", label="stress-analysis")
            writer.add_text("As shown in @tbl-stress-analysis...")
        """
        super().add_colored_table(df, title, show_figure,
                                  highlight_columns=highlight_columns, palette_name=palette_name,
                                  max_rows_per_table=max_rows_per_table, hide_columns=hide_columns,
                                  filter_by=filter_by, sort_by=sort_by, width_inches=width_inches, label=label)
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
        
        Quarto standard callout type.
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
        
        Quarto standard callout type.
        Shortcut for add_callout(content, type="warning", title=title).
        
        Args:
            content: Warning text content. Supports markdown formatting.
            title: Warning title. If None, uses "Warning" as default.
        
        Returns:
            Self for method chaining.
        """
        return self.add_callout(content, type="warning", title=title)
        
    def add_caution(self, content: str, title: str = None) -> 'DocumentWriter':
        """Add caution callout (orange styling) for cautionary information.
        
        Quarto standard callout type.
        Shortcut for add_callout(content, type="caution", title=title).
        
        Args:
            content: Caution text content. Supports markdown formatting.
            title: Caution title. If None, uses "Caution" as default.
        
        Returns:
            Self for method chaining.
        """
        return self.add_callout(content, type="caution", title=title)
        
    def add_important(self, content: str, title: str = None) -> 'DocumentWriter':
        """Add important callout (red/pink styling) for critical information.
        
        Quarto standard callout type.
        Shortcut for add_callout(content, type="important", title=title).
        
        Args:
            content: Important text content. Supports markdown formatting.
            title: Important title. If None, uses "Important" as default.
        
        Returns:
            Self for method chaining.
        """
        return self.add_callout(content, type="important", title=title)
        
    def add_plot(self, fig, title: str = None, caption: str = None, source: str = None, 
                 palette_name: str = None, show_figure: bool = False, label: str = None) -> 'DocumentWriter':
        """Add plot.
        
        Args:
            fig: Matplotlib figure object.
            title: Plot title.
            caption: Plot caption.
            source: Source information.
            palette_name: Color palette for plot colors (e.g., 'blues', 'reds', 'minimal').
                         If specified, matplotlib will use only colors from this palette.
                         If None, matplotlib uses its default color cycle.
            show_figure: If True, displays the generated plot image immediately in Jupyter notebooks
                        for interactive development. Default False. The plot is always included in 
                        the final document regardless of this setting.
            label: Optional Quarto label for cross-referencing (e.g., 'myplot').
                  When provided, enables references like @fig-myplot in text.
                  Without this, the plot gets auto-generated ID like fig-1.
        
        Returns:
            Self for method chaining.
            
        Example:
            writer.add_plot(fig, title="Stress Distribution", caption="Results from FEA")
            writer.add_plot(fig, title="Analysis", label="stress-plot")
            writer.add_text("As shown in @fig-stress-plot...")
        """
        super().add_plot(fig, title, caption, source, palette_name=palette_name, show_figure=show_figure, label=label)
        return self
        
    def add_image(self, path: str, caption: str = None, width: str = None,
                  alt_text: str = None, responsive: bool = True, label: str = None) -> 'DocumentWriter':
        """Add image from file with automatic path resolution.
        
        Args:
            path: Path to image file. Supports:
                 - Absolute paths: "/path/to/image.png"
                 - Relative paths: "images/figure.png" (relative to document)
                 - Remote URLs: "https://example.com/image.jpg"
                 Supported formats: PNG, JPG, JPEG, SVG, PDF
            caption: Image caption/title. If None, no caption is added.
            width: Image width specification: "80%" or "6in". If None, uses 100%.
            alt_text: Alternative text for accessibility (used in HTML alt attribute).
            responsive: If True (default), image scales responsively in HTML output.
            label: Optional Quarto label for cross-referencing (e.g., 'fig-myimage').
                  When provided, enables references like @fig-myimage in text.
                  Without this, the image gets auto-generated ID like fig-1.
            
        Returns:
            Self for method chaining.
            
        Example:
            writer.add_image("results/plot.png", caption="Stress distribution")
            writer.add_image("logo.svg", width="50%")
            writer.add_image("diagram.pdf", alt_text="System diagram", responsive=True)
            writer.add_image("chart.png", caption="Results", label="fig-results")
            writer.add_text("As shown in @fig-results...")
        """
        super().add_image(path, caption, width,
                          alt_text=alt_text, responsive=responsive, label=label)
        return self
        
    def add_reference_to_element(self, ref_type: str, label: str, custom_text: str = None) -> 'DocumentWriter':
        """Add cross-reference to tables, figures, or equations.
        
        Creates a clickable reference to previously defined elements in the document.
        The label must match the label assigned when creating the element.
        
        Args:
            ref_type: Type of reference. Options:
                     - "table" or "tbl": References to tables
                     - "figure" or "fig": References to figures/plots
                     - "equation" or "eq": References to equations
            label: Reference label identifier that matches the label used when creating the element.
                  Examples:
                  - For tables: "results", "stress-data" (matches label in add_table)
                  - For figures: "stress-plot", "diagram" (matches label in add_plot/add_image)
                  - For equations: "einstein", "pythagorean" (matches label in add_equation)
                  Note: Do NOT include prefixes like 'tbl-', 'fig-', 'eq-' - just the label.
            custom_text: Custom reference text. If None, uses auto-generated text
                        (e.g., "Table 1", "Figure 2", "Equation 3").
        
        Returns:
            Self for method chaining.
            
        Example:
            # Add table with label
            writer.add_table(df, title="Results", label="results")
            
            # Reference the table
            writer.add_text("As shown in ")
            writer.add_reference_to_element("table", "results")
            writer.add_text(", the values are significant.")
            # Renders as: "As shown in Table 1, the values are significant."
            
            # Add plot with label and reference it
            writer.add_plot(fig, title="Stress Analysis", label="stress-plot")
            writer.add_reference_to_element("fig", "stress-plot", custom_text="the stress plot")
            # Renders as: "the stress plot" (clickable link to figure)
            
            # Multiple references
            writer.add_equation("E = mc^2", caption="Einstein", label="einstein")
            writer.add_text("According to ")
            writer.add_reference_to_element("equation", "einstein")
            # Renders as: "According to Equation 1"
        """
        super().add_reference(ref_type, label, custom_text)
        return self
        
    def add_reference_citation(self, citation_key: str, page: str = None) -> 'DocumentWriter':
        """Add bibliographic citation from bibliography file.
        
        Requires bibliography file specified in project configuration or passed to generate().
        
        NOTE: This method generates [@citation_key] markdown. If you already included 
        [@citation_key] directly in your text (which is the recommended approach for 
        inline citations), DO NOT call this method again as it will create duplicates.
        
        Use this method when:
        - You want to add a citation separately after a paragraph
        - You need programmatic citation insertion
        
        Use inline [@key] when:
        - Citations are part of sentences (recommended)
        - Multiple citations in lists or content
        
        Args:
            citation_key: Citation key from bibliography file (e.g., "Einstein1905").
                         Do NOT include [@...] brackets - just the key.
            page: Specific page number(s) for the citation (e.g., "42" or "15-20").
                 Optional. If provided, formats as [@Author2020, p. 42].
        
        Returns:
            Self for method chaining.
            
        Example:
            # Option 1: Inline (recommended)
            writer.add_text("According to the standard [@CSCR2010_14], the design...")
            
            # Option 2: Separate method
            writer.add_text("According to the standard, the design...")
            writer.add_citation("CSCR2010_14")
            
            # With page number
            writer.add_text("The coefficient is defined as ")
            writer.add_citation("Smith2020", page="127")
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
    
    def reset(self) -> 'DocumentWriter':
        """Reset the document to allow creating new content after generation.
        
        This method clears all content, resets counters, and clears project information,
        allowing the same DocumentWriter instance to be reused for creating multiple documents.
        
        Returns:
            Self for method chaining.
            
        Example:
            writer = DocumentWriter('report')
            writer.add_h1("First Document")
            output1 = writer.generate('html')
            
            # Reset and create second document
            writer.reset()
            writer.add_h1("Second Document") 
            output2 = writer.generate('html')
        """
        # Reset the core document state
        super().reset_document()
        
        return self

