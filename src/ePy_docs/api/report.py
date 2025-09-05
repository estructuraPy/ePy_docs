import os
from typing import Dict, List, Any, Optional, Union, Tuple

import pandas as pd
import matplotlib.pyplot as plt
from pydantic import Field

from ePy_docs.components.base import WriteFiles
from ePy_docs.components.notes import NoteRenderer
from ePy_docs.components.text import get_text_config
from ePy_docs.components.pages import get_layout_name
from ePy_docs.components.setup import _load_cached_files, _resolve_config_path, get_absolute_output_directories
from ePy_docs.components.project_info import get_project_config_data
# PURIFIED: Use official commercial office for display
from ePy_docs.components.images import display_in_notebook

def process_mathematical_text(latex_code, layout_name, sync_files):
    """Mathematical text processing compatibility function."""
    return latex_code

class ReportWriter(WriteFiles):
    """Clean writer for technical reports - all configuration from JSON files.
    
    Automatically constructs file paths from setup.json and project_info.json.
    No hardcoded values, no fallbacks, no verbose output.
    Configuration must exist in components/*.json files.
    
    IMPORTANTE: Use ONLY add_colored_table() for tables.
    The old add_table() function has been EXILED to DIMENSION ESPEJO
    for violating DIMENSIÓN TRANSPARENCIA (contained HTML fallbacks).
    """
    
    model_config = {"arbitrary_types_allowed": True}

    table_counter: int = Field(default=0)
    figure_counter: int = Field(default=0)
    output_dir: str = Field(default="")
    show_in_notebook: bool = Field(default=True)
    sync_files: bool = Field(default=False)
    layout_style: str = Field(default="corporate")
    note_renderer: Optional[NoteRenderer] = Field(default=None)

    def __init__(self, sync_files: bool = True, **data):
        """Initialize ReportWriter using JSON configurations only.
        
        Args:
            sync_files: Whether to use synchronized configuration files
        """
        # Ensure sync_files is in data
        data['sync_files'] = sync_files
        
        # Initialize with layout_style if not provided
        layout_style = data.get('layout_style', 'corporate')
        
        # Create note_renderer with proper layout_style
        if 'note_renderer' not in data or data['note_renderer'] is None:
            data['note_renderer'] = NoteRenderer(layout_style=layout_style, sync_files=sync_files)
        
        # Get configurations from JSON files with absolute paths respecting sync_files
        output_dirs = get_absolute_output_directories(sync_files)
        project_config = get_project_config_data(sync_files=sync_files)
        
        # Get layout style from current configuration - REQUIRED according to DIMENSIÓN TRANSPARENCIA
        from ePy_docs.components.pages import get_current_layout
        try:
            layout_style = get_current_layout()
            data['layout_style'] = layout_style
        except RuntimeError:
            # If no layout is set, use 'corporate' as DIMENSIÓN-compliant default
            data['layout_style'] = 'corporate'
        
        # Construct file_path automatically from configurations
        report_name = project_config['project']['report']
        report_dir = output_dirs['report']
        auto_file_path = os.path.join(report_dir, f"{report_name}.md")
        
        # Use auto-generated file_path if not provided
        if 'file_path' not in data:
            data['file_path'] = auto_file_path
            
        super().__init__(**data)
        self.file_path = os.path.abspath(self.file_path)
        
        # Use absolute report directory from setup.json
        self.output_dir = os.path.abspath(report_dir)
        os.makedirs(self.output_dir, exist_ok=True)

    def get_content(self) -> str:
        """Get the complete accumulated content as a single string.
        
        Returns:
            All content in content_buffer joined together
        """
        return ''.join(self.content_buffer)

    # Headers - SIMPLIFIED VERSION using basic markdown
    def add_h1(self, text: str) -> None:
        """Add H1 header using basic markdown."""
        self.add_content(f"# {text}\n\n")

    def add_h2(self, text: str) -> None:
        """Add H2 header using basic markdown."""
        self.add_content(f"## {text}\n\n")

    def add_h3(self, text: str) -> None:
        """Add H3 header using basic markdown."""
        self.add_content(f"### {text}\n\n")

    # Text and lists
    def add_text(self, content: str) -> None:
        """Add text content."""
        # Direct content addition - Reino TEXT provides specific formatting functions for headers
        # For regular text, use content as-is to maintain simplicity
        self.add_content(content)

    def add_list(self, items: List[str], ordered: bool = False) -> None:
        """Add bulleted or numbered list."""
        # Simple list formatting without Reino TEXT dependency
        if ordered:
            # Numbered list
            formatted_items = [f"{i+1}. {item}" for i, item in enumerate(items)]
        else:
            # Bulleted list
            formatted_items = [f"- {item}" for item in items]
        
        list_content = '\n'.join(formatted_items) + '\n'
        self.add_content(list_content)

    # Code chunks
    def add_chunk(self, code: str, language: str = 'python', 
                  caption: Optional[str] = None, label: Optional[str] = None) -> None:
        """Add non-executable code chunk to report (display only).
        
        Args:
            code: Code content as multiline string
            language: Programming language (python, javascript, sql, etc.)
            caption: Optional caption for the code block
            label: Optional label for cross-referencing
        """
        from ePy_docs.components.code import format_display_chunk
        
        chunk_content = format_display_chunk(code, language, caption, label)
        self.add_content(chunk_content)

    def add_chunk_executable(self, code: str, language: str = 'python', 
                            caption: Optional[str] = None, label: Optional[str] = None) -> None:
        """Add executable code chunk to report (will be executed by Quarto).
        
        Args:
            code: Code content as multiline string
            language: Programming language (python, javascript, r, etc.)
            caption: Optional caption for the code block
            label: Optional label for cross-referencing
        """
        from ePy_docs.components.code import format_executable_chunk
        
        chunk_content = format_executable_chunk(code, language, caption, label)
        self.add_content(chunk_content)

    # Tables - Configuration from tables.json only
    def add_table(self, df: pd.DataFrame, title: str = None,
                  hide_columns: Union[str, List[str]] = None,
                  filter_by: Union[Tuple, List[Tuple]] = None,
                  sort_by: Union[str, Tuple, List] = None,
                  max_rows_per_table: Optional[Union[int, List[int]]] = None,
                  palette_name: Optional[str] = None,
                  n_rows: Optional[Union[int, List[int]]] = None,
                  source: Optional[str] = None) -> None:
        """PURIFIED add_table - Simple case of add_colored_table without highlights.
        
        This is a clean wrapper around add_colored_table that respects all DIMENSIONES RECTORAS.
        No fallbacks, no mercado negro, pure configuration from JSON files.
        """
        # Delegate to add_colored_table with no highlights - PURE DIMENSIÓN TRANSPARENCIA
        self.add_colored_table(
            df=df,
            title=title,
            highlight_columns=None,  # NO HIGHLIGHTS - simple table
            hide_columns=hide_columns,
            filter_by=filter_by,
            sort_by=sort_by,
            max_rows_per_table=max_rows_per_table,
            palette_name=palette_name,
            n_rows=n_rows,
            source=source
        )

    def add_colored_table(self, df: pd.DataFrame, title: str = None,
                          highlight_columns: Optional[List[str]] = None,
                          hide_columns: Union[str, List[str]] = None,
                          filter_by: Union[Tuple, List[Tuple]] = None,
                          sort_by: Union[str, Tuple, List] = None,
                          max_rows_per_table: Optional[Union[int, List[int]]] = None,
                          palette_name: Optional[str] = None,
                          n_rows: Optional[Union[int, List[int]]] = None,
                          source: Optional[str] = None) -> None:
        """Add colored table to report using REINO TABLES puro.
        
        Args:
            df: DataFrame to process.
            title: Table title.
            highlight_columns: Columns to highlight (not yet implemented).
            hide_columns: Columns to hide from display.
            filter_by: Filter criteria for rows.
            sort_by: Sort criteria.
            max_rows_per_table: Maximum rows per table.
            palette_name: Color palette (not yet implemented).
            n_rows: Number of rows to display.
            source: Data source attribution.
        """
        from ePy_docs.components.tables import process_table_for_report
        
        # Process DataFrame
        processed_df = df.copy()
        
        # Apply hiding columns
        if hide_columns:
            columns_to_hide = [hide_columns] if isinstance(hide_columns, str) else hide_columns
            processed_df = processed_df.drop(columns=[col for col in columns_to_hide if col in processed_df.columns])
        
        # Apply filtering - PURIFIED: Handle single values and lists properly
        if filter_by:
            filters = [filter_by] if isinstance(filter_by, tuple) else filter_by
            for column, values in filters:
                if column in processed_df.columns:
                    if isinstance(values, (list, tuple)):
                        # Multiple values: use isin for proper filtering
                        processed_df = processed_df[processed_df[column].isin(values)]
                    else:
                        # Single value: direct comparison
                        processed_df = processed_df[processed_df[column] == values]
        
        # Apply sorting
        if sort_by:
            if isinstance(sort_by, str):
                processed_df = processed_df.sort_values(sort_by)
            elif isinstance(sort_by, tuple) and len(sort_by) == 2:
                column, order = sort_by
                ascending = order.lower() in ['asc', 'ascending']
                processed_df = processed_df.sort_values(column, ascending=ascending)
        
        # Apply row limiting
        if n_rows:
            processed_df = processed_df.head(n_rows)
        elif max_rows_per_table:
            row_limit = max_rows_per_table[0] if isinstance(max_rows_per_table, list) else max_rows_per_table
            processed_df = processed_df.head(row_limit)
        
        # Generate table using REINO TABLES
        self.table_counter += 1
        
        image_path, figure_id = process_table_for_report(
            data=processed_df,
            title=title,
            output_dir=self.output_dir,
            figure_counter=self.table_counter,
            layout_style=self.layout_style,
            sync_files=False,
            highlight_columns=highlight_columns,
            palette_name=palette_name
        )
        
        # Format table for report
        caption_with_source = f": {title}"
        if source:
            caption_with_source += f" {source}"
        
        table_markdown = f"![Table {self.table_counter}{caption_with_source}]({image_path})\n\n"
        
        # Add to content using pure WriteFiles method
        self.add_content(table_markdown)
        
        # Display in notebook using official REINO IMAGES function
        display_in_notebook(image_path, self.show_in_notebook)

    # Figures and Images - Configuration from images.json only
    def add_plot(self, fig: plt.Figure, title: str = None, caption: str = None, source: str = None) -> str:
        """Add matplotlib plot to report using images.json configuration."""
        from ePy_docs.components.images import save_plot_image, format_figure_markdown
        
        self.figure_counter += 1
        
        # Save plot image using images.json configuration
        img_path = save_plot_image(fig, self.output_dir, self.figure_counter)
        
        # Format figure markdown using images.json configuration
        figure_markdown = format_figure_markdown(
            img_path, self.figure_counter, title, caption, source
        )
        
        self.add_content(figure_markdown)
        display_in_notebook(img_path, self.show_in_notebook)
        
        return img_path

    def add_image(self, path: str, caption: str = None, width: str = None,
                  alt_text: str = None, align: str = None, label: str = None, source: str = None) -> str:
        """Add external image to report using images.json configuration."""
        from ePy_docs.components.images import copy_and_process_image, format_image_markdown
        
        self.figure_counter += 1
        
        # Copy and process image using images.json configuration
        dest_path = copy_and_process_image(path, self.output_dir, self.figure_counter)
        
        # Format image markdown using images.json configuration
        figure_markdown, figure_id = format_image_markdown(
            dest_path, self.figure_counter, caption, width, alt_text, align, label, source, self.output_dir
        )
        
        self.add_content(figure_markdown)
        display_in_notebook(dest_path, self.show_in_notebook)
        
        return figure_id

    # Notes and Callouts - Clean API using notes.py
    def add_note(self, content: str, title: str = None) -> str:
        """Add informational note callout with visual display."""
        # Show visual callout in notebook
        self.note_renderer.display_callout(content, "note", title)
        # Add Quarto markdown to content buffer for final document
        callout_markdown = self.note_renderer.create_note_markdown(content, "note", title)
        self.add_content(callout_markdown)
        return "note"

    def add_tip(self, content: str, title: str = None) -> str:
        """Add tip callout with visual display."""
        # Show visual callout in notebook
        self.note_renderer.display_callout(content, "tip", title)
        # Add Quarto markdown to content buffer for final document
        callout_markdown = self.note_renderer.create_note_markdown(content, "tip", title)
        self.add_content(callout_markdown)
        return "tip"

    def add_warning(self, content: str, title: str = None) -> str:
        """Add warning callout with visual display."""
        # Show visual callout in notebook
        self.note_renderer.display_callout(content, "warning", title)
        # Add Quarto markdown to content buffer for final document
        callout_markdown = self.note_renderer.create_note_markdown(content, "warning", title)
        self.add_content(callout_markdown)
        return "warning"

    def add_error(self, content: str, title: str = None) -> str:
        """Add error callout with visual display."""
        self.note_renderer.display_callout(content, "error", title)
        callout_markdown = self.note_renderer.create_note_markdown(content, "error", title)
        self.add_content(callout_markdown)
        return "error"
        
    def add_success(self, content: str, title: str = None) -> str:
        """Add success callout with visual display."""
        self.note_renderer.display_callout(content, "success", title)
        callout_markdown = self.note_renderer.create_note_markdown(content, "success", title)
        self.add_content(callout_markdown)
        return "success"

    def add_caution(self, content: str, title: str = None) -> str:
        """Add caution callout with visual display."""
        self.note_renderer.display_callout(content, "caution", title)
        callout_markdown = self.note_renderer.create_note_markdown(content, "caution", title)
        self.add_content(callout_markdown)
        return "caution"

    def add_important(self, content: str, title: str = None) -> str:
        """Add important callout with visual display."""
        self.note_renderer.display_callout(content, "important", title)
        callout_markdown = self.note_renderer.create_note_markdown(content, "important", title)
        self.add_content(callout_markdown)
        return "important"

    def add_information(self, content: str, title: str = None) -> str:
        """Add information callout with visual display."""
        self.note_renderer.display_callout(content, "info", title)
        callout_markdown = self.note_renderer.create_note_markdown(content, "info", title)
        self.add_content(callout_markdown)
        return "info"

    def add_recommendation(self, content: str, title: str = None) -> str:
        """Add recommendation callout with visual display."""
        self.note_renderer.display_callout(content, "rec", title)
        callout_markdown = self.note_renderer.create_note_markdown(content, "rec", title)
        self.add_content(callout_markdown)
        return "rec"

    def add_advice(self, content: str, title: str = None) -> str:
        """Add advice callout with visual display."""
        self.note_renderer.display_callout(content, "advice", title)
        callout_markdown = self.note_renderer.create_note_markdown(content, "advice", title)
        self.add_content(callout_markdown)
        return "advice"

    def add_risk(self, content: str, title: str = None) -> str:
        """Add risk callout with visual display."""
        self.note_renderer.display_callout(content, "risk", title)
        callout_markdown = self.note_renderer.create_note_markdown(content, "risk", title)
        self.add_content(callout_markdown)
        return "risk"

    # Equations
    def add_equation(self, latex_code: str, caption: str = None, label: str = None) -> str:
        """Add numbered block equation."""
        from ePy_docs.components.pages import get_layout_name
        
        layout_name = get_layout_name(sync_files=self.sync_files)
        processed_equation = process_mathematical_text(latex_code, layout_name, self.sync_files)
        
        # Format as block equation with label and caption
        if label is None:
            label = f"eq:equation_{self.figure_counter + 1}"
        
        equation_markdown = f"$${processed_equation}$$ {{#{label}}}"
        if caption:
            equation_markdown += f"\n\n: {caption}"
            
        self.add_content(equation_markdown)
        return label

    def add_equation_in_line(self, latex_code: str) -> None:
        """Add inline equation (not numbered)."""
        from ePy_docs.components.pages import get_layout_name
        
        layout_name = get_layout_name(sync_files=self.sync_files)
        processed_equation = process_mathematical_text(latex_code, layout_name, self.sync_files)
        
        # For inline equations, we add them as part of text content without line breaks
        inline_equation = f"${processed_equation}$"
        
        # Add to content buffer but format as inline (no double newlines)
        if inline_equation:
            if not inline_equation.endswith(' '):
                inline_equation = inline_equation + ' '
            # Get the last content and append to it if it doesn't end with newlines
            if self.content_buffer and not self.content_buffer[-1].endswith('\n\n'):
                self.content_buffer[-1] = self.content_buffer[-1].rstrip() + inline_equation
            else:
                self.content_buffer.append(inline_equation)

    def add_equation_block(self, equations: List[str], caption: str = None,
                          label: str = None, align: bool = True) -> str:
        """Add block of multiple aligned equations."""
        from ePy_docs.components.pages import get_layout_name
        
        layout_name = get_layout_name(sync_files=self.sync_files)
        
        if label is None:
            label = f"eq:equations_{self.figure_counter + 1}"
        
        # Process each equation
        processed_equations = [process_mathematical_text(eq, layout_name, self.sync_files) 
                             for eq in equations]
        
        # Format as aligned block
        if align:
            equations_text = " \\\\\n".join(processed_equations)
            equation_markdown = f"$$\\begin{{aligned}}\n{equations_text}\n\\end{{aligned}}$$ {{#{label}}}"
        else:
            equations_text = " \\\\\n".join(processed_equations)
            equation_markdown = f"$$\\begin{{gather}}\n{equations_text}\n\\end{{gather}}$$ {{#{label}}}"
            
        if caption:
            equation_markdown += f"\n\n: {caption}"
            
        self.add_content(equation_markdown)
        return label

    def add_reference(self, ref_type: str, ref_id: str, custom_text: str = None) -> str:
        """Add cross-reference to figure, table, equation, or note."""
        from ePy_docs.components.references import format_cross_reference
        
        if ref_type == 'note':
            reference = self.note_renderer.create_cross_reference(ref_id, custom_text)
        else:
            reference = format_cross_reference(ref_type, ref_id, custom_text)
        
        self.add_content(reference)
        return reference

    def add_citation(self, citation_key: str, page: str = None) -> str:
        """Add inline citation."""
        from ePy_docs.components.references import format_citation
        
        citation = format_citation(citation_key, page)
        self.add_inline_content(citation)
        return citation

    # File import methods - include external files in the current document
    def add_quarto_file(self, file_path: str, include_yaml: bool = False, fix_image_paths: bool = True) -> None:
        """Import and include content from an existing Quarto (.qmd) file.
        
        Args:
            file_path: Path to the .qmd file to import
            include_yaml: Whether to include YAML frontmatter (default: False)
            fix_image_paths: Whether to automatically fix image paths (default: True)
        """
        from ePy_docs.files.importer import process_quarto_file, format_imported_content
        
        content, self.figure_counter = process_quarto_file(
            file_path=file_path,
            include_yaml=include_yaml,
            fix_image_paths=fix_image_paths,
            output_dir=self.output_dir,
            figure_counter=self.figure_counter
        )
        
        formatted_content = format_imported_content(content)
        self.add_content(formatted_content)

    def add_markdown_file(self, file_path: str, fix_image_paths: bool = True) -> None:
        """Import and include content from an existing Markdown (.md) file.
        
        Args:
            file_path: Path to the .md file to import
            fix_image_paths: Whether to automatically fix image paths (default: True)
        """
        from ePy_docs.files.importer import process_markdown_file, format_imported_content
        
        content, self.figure_counter = process_markdown_file(
            file_path=file_path,
            fix_image_paths=fix_image_paths,
            output_dir=self.output_dir,
            figure_counter=self.figure_counter
        )
        
        formatted_content = format_imported_content(content)
        self.add_content(formatted_content)

    # Document Generation
    def generate(self, markdown: bool = False, html: bool = False, pdf: bool = False, 
                qmd: bool = False, tex: bool = False,
                output_filename: str = None) -> None:
        """Generate report in requested formats using clean JSON-only configuration.
        
        Args:
            markdown: Generate .md file (uses clean generator if only markdown/html/pdf)
            html: Generate .html file
            pdf: Generate .pdf file
            qmd: Generate .qmd file (Quarto Markdown)
            tex: Generate .tex file (LaTeX)
            output_filename: Custom filename for output files (without extension)
        """
        
        # Prepare content
        content = ''.join(self.content_buffer)
        
        # Use clean generator for HTML/PDF only (no legacy features)
        if (html or pdf) and not (markdown or qmd or tex):
            from ePy_docs.components.generator import generate_documents_clean
            from ePy_docs.components.project_info import get_project_config_data
            
            # Get project title from configuration
            project_config = get_project_config_data(sync_files=self.sync_files)
            title = project_config['project']['name']  # Use 'name' instead of 'title'
            
            generate_documents_clean(
                content=content,
                title=title,
                html=html,
                pdf=pdf,
                output_filename=output_filename,
                sync_files=self.sync_files
            )
        else:
            # Use original generator for backward compatibility with markdown/qmd/tex
            from ePy_docs.components.generator import generate_documents
            
            generate_documents(
                content=content,
                file_path=self.file_path,
                markdown=markdown,
                html=html,
                pdf=pdf,
                qmd=qmd,
                tex=tex,
                output_filename=output_filename,
                sync_files=self.sync_files,
                output_dir=self.output_dir
            )

