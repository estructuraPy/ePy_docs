import os
import tempfile
import shutil
from typing import Dict, List, Any, Optional, Union, Tuple

import pandas as pd
import matplotlib.pyplot as plt
from pydantic import Field

from ePy_docs.core.base import WriteFiles
from ePy_docs.components.tables import create_table_image, create_split_table_images
from ePy_docs.components.images import ImageProcessor, display_in_notebook
from ePy_docs.components.notes import NoteRenderer
from ePy_docs.components.equations import EquationProcessor
from ePy_docs.components.page import get_full_project_config


class ReportWriter(WriteFiles):
    """Clean writer for technical reports focused on user content creation.
    
    Provides essential methods for creating report content including:
    - Headers (H1, H2, H3)
    - Text content and lists
    - Tables (simple and colored)
    - Figures and images
    - Equations (inline and numbered blocks)
    - Notes and callouts
    - References and citations
    
    All configuration comes from JSON files, no hardcoded values or fallbacks.
    """
    
    model_config = {"arbitrary_types_allowed": True}

    table_counter: int = Field(default=0)
    figure_counter: int = Field(default=0)
    note_counter: int = Field(default=0)
    output_dir: str = Field(default="")
    show_in_notebook: bool = Field(default=True, description="Whether to display images in Jupyter notebooks")
    note_renderer: NoteRenderer = Field(default_factory=NoteRenderer)
    equation_processor: EquationProcessor = Field(default_factory=EquationProcessor)

    def __init__(self, **data):
        """Initialize ReportWriter with directory setup."""
        super().__init__(**data)
        self.file_path = os.path.abspath(self.file_path)
        
        if not self.output_dir:
            self.output_dir = os.path.dirname(self.file_path)
        else:
            self.output_dir = os.path.abspath(self.output_dir)
        
        os.makedirs(self.output_dir, exist_ok=True)


    # Headers
    def add_h1(self, text: str) -> None:
        """Add H1 header."""
        from ePy_docs.components.text import format_header_h1
        
        formatted_header = format_header_h1(text)
        self.add_content(formatted_header)

    def add_h2(self, text: str) -> None:
        """Add H2 header."""
        from ePy_docs.components.text import format_header_h2
        
        formatted_header = format_header_h2(text)
        self.add_content(formatted_header)

    def add_h3(self, text: str) -> None:
        """Add H3 header."""
        from ePy_docs.components.text import format_header_h3
        
        formatted_header = format_header_h3(text)
        self.add_content(formatted_header)

    # Text and lists
    def add_text(self, content: str) -> None:
        """Add text content."""
        from ePy_docs.components.text import format_text_content
        
        formatted_content = format_text_content(content)
        self.add_content(formatted_content)

    def add_list(self, items: List[str], ordered: bool = False) -> None:
        """Add bulleted or numbered list."""
        from ePy_docs.components.text import format_list
        
        formatted_list = format_list(items, ordered)
        self.add_content(formatted_list)

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

    # Tables
    def add_table(self, df: pd.DataFrame, title: str = None,
                  hide_columns: Union[str, List[str]] = None,
                  filter_by: Union[Tuple, List[Tuple]] = None,
                  sort_by: Union[str, Tuple, List] = None,
                  max_rows_per_table: Optional[Union[int, List[int]]] = None,
                  palette_name: Optional[str] = None,
                  n_rows: Optional[Union[int, List[int]]] = None,
                  source: Optional[str] = None) -> None:
        """Add simple table to report.
        
        Args:
            palette_name: Optional color palette for table (not used in simple tables, kept for API consistency)
            n_rows: Take only the first N rows from the DataFrame (subset)
            source: Optional source information for the table
        """
        from ePy_docs.components.tables import add_table_to_content
        
        markdown_list, self.table_counter = add_table_to_content(
            df=df, output_dir=self.output_dir, table_counter=self.table_counter,
            title=title, hide_columns=hide_columns, filter_by=filter_by,
            sort_by=sort_by, max_rows_per_table=max_rows_per_table, n_rows=n_rows,
            source=source
        )
        
        for table_markdown, img_path in markdown_list:
            self.add_content(table_markdown)
            display_in_notebook(img_path, self.show_in_notebook)

    def add_colored_table(self, df: pd.DataFrame, title: str = None,
                          highlight_columns: Optional[List[str]] = None,
                          hide_columns: Union[str, List[str]] = None,
                          filter_by: Union[Tuple, List[Tuple]] = None,
                          sort_by: Union[str, Tuple, List] = None,
                          max_rows_per_table: Optional[Union[int, List[int]]] = None,
                          palette_name: Optional[str] = None,
                          n_rows: Optional[Union[int, List[int]]] = None,
                          source: Optional[str] = None) -> None:
        """Add colored table to report.
        
        Args:
            n_rows: Take only the first N rows from the DataFrame (subset)
            source: Optional source information for the table
        """
        from ePy_docs.components.tables import add_colored_table_to_content
        
        markdown_list, self.table_counter = add_colored_table_to_content(
            df=df, output_dir=self.output_dir, table_counter=self.table_counter,
            title=title, highlight_columns=highlight_columns, hide_columns=hide_columns,
            filter_by=filter_by, sort_by=sort_by, max_rows_per_table=max_rows_per_table,
            palette_name=palette_name, n_rows=n_rows, source=source
        )
        
        for table_markdown, img_path in markdown_list:
            self.add_content(table_markdown)
            display_in_notebook(img_path, self.show_in_notebook)

    # Figures and Images
    def add_plot(self, fig: plt.Figure, title: str = None, caption: str = None, source: str = None) -> str:
        """Add matplotlib plot to report."""
        project_config = get_full_project_config()
        
        # Get figures config - no fallbacks
        figures_config = project_config['styling']['figures']
        
        self.figure_counter += 1
        
        figures_dir = os.path.join(self.output_dir, "figures")
        os.makedirs(figures_dir, exist_ok=True)
        
        img_filename = f"figure_{self.figure_counter}.png"
        img_path = os.path.join(figures_dir, img_filename)
        
        fig.savefig(img_path, bbox_inches='tight', dpi=figures_config['dpi'], 
                   facecolor='white', edgecolor='none')
        
        rel_path = ImageProcessor.get_relative_path(img_path, self.output_dir)
        figure_id = f"fig-{self.figure_counter}"
        
        final_caption = caption or title
        
        # Integrate source into caption if provided
        if source:
            try:
                from ePy_docs.components.page import _ConfigManager
                config_manager = _ConfigManager()
                image_config = config_manager.get_config_by_path('components/images.json')
                source_config = image_config.get('source', {})
                
                if source_config.get('enable_source', True):
                    source_text = source_config.get('source_format', '({source})').format(source=source)
                    if final_caption:
                        final_caption = f"{final_caption} {source_text}"
                    else:
                        final_caption = source_text
            except:
                # Fallback if config is not available
                if final_caption:
                    final_caption = f"{final_caption} ({source})"
                else:
                    final_caption = f"({source})"
        
        if final_caption:
            content = f"\n\n![]({rel_path}){{#{figure_id}}}\n\n: {final_caption}\n\n"
        else:
            content = f"\n\n![]({rel_path}){{#{figure_id}}}\n\n"
        
        self.add_content(content)
        
        return img_path

    def add_image(self, path: str, caption: str = None, width: str = None,
                  alt_text: str = None, align: str = None, label: str = None, source: str = None) -> str:
        """Add external image to report with proper numbering and cross-reference support.
        
        Args:
            path: Path to the image file
            caption: Optional caption for the image  
            width: Width specification for Quarto format
            alt_text: Alternative text for the image
            align: Alignment for Quarto format
            label: Optional custom label for cross-referencing. If None, uses sequential numbering
            source: Optional source information for the image
            
        Returns:
            The figure label used for cross-referencing
        """
        self.figure_counter += 1
        
        # Create figures directory
        figures_dir = os.path.join(self.output_dir, "figures")
        os.makedirs(figures_dir, exist_ok=True)
        
        # Get file extension and create new filename with figure numbering
        _, ext = os.path.splitext(path)
        new_filename = f"figure_{self.figure_counter}{ext}"
        dest_path = os.path.join(figures_dir, new_filename)
        
        # Copy file to destination with new name
        shutil.copy2(path, dest_path)
        
        # Get relative path for markdown
        rel_path = ImageProcessor.get_relative_path(dest_path, self.output_dir)
        
        # Create figure label - use custom label if provided, otherwise use sequential numbering
        if label is None:
            figure_id = f"fig-{self.figure_counter}"
        else:
            # Use custom label but ensure it follows fig- convention for cross-references
            if not label.startswith('fig-'):
                figure_id = f"fig-{label}"
            else:
                figure_id = label
        
        # Load image configuration for proper formatting (like tables do)
        try:
            from ePy_docs.components.page import _ConfigManager
            config_manager = _ConfigManager()
            image_config = config_manager.get_config_by_path('components/images.json')
            
            # Create figure caption using the same logic as tables
            if caption:
                fig_caption = image_config['pagination']['figure_title_format'].format(title=caption)
            else:
                fig_caption = image_config['pagination']['figure_no_title_format'].format(counter=self.figure_counter)
                
            # Integrate source into caption if provided
            if source:
                try:
                    source_config = image_config.get('source', {})
                    if source_config.get('enable_source', True):
                        source_text = source_config.get('source_format', '({source})').format(source=source)
                        if fig_caption:
                            fig_caption = f"{fig_caption} {source_text}"
                        else:
                            fig_caption = source_text
                except:
                    # Fallback if config is not available
                    if fig_caption:
                        fig_caption = f"{fig_caption} ({source})"
                    else:
                        fig_caption = f"({source})"
        except:
            # Fallback if config is not available
            if caption:
                fig_caption = caption
            else:
                fig_caption = f"Figura {self.figure_counter}"
        
        # Override with custom alt text if provided
        if alt_text:
            fig_caption = alt_text
        
        # Build attributes list
        attributes = [f'#{figure_id}']
        if width:
            attributes.append(f'fig-width="{width}"')
        if align:
            attributes.append(f'fig-align="{align}"')
        
        # Create image markdown using EXACTLY the same format as tables
        img_markdown = f"\n\n![{fig_caption}]({rel_path}){{{' '.join(attributes)}}}\n\n"
        
        # Add to content
        self.add_content(img_markdown)
        
        # Display image in notebook if available
        display_in_notebook(dest_path, self.show_in_notebook)
        
        return figure_id

    # Notes and Callouts
    def add_note(self, content: str, title: str = None) -> str:
        """Add informational note callout."""
        callout = self.note_renderer.create_quarto_callout(content, "note", title)
        self.add_content(f"\n\n{callout['markdown']}\n\n")
        return callout['ref_id']

    def add_tip(self, content: str, title: str = None) -> str:
        """Add tip callout."""
        callout = self.note_renderer.create_quarto_callout(content, "tip", title)
        self.add_content(f"\n\n{callout['markdown']}\n\n")
        return callout['ref_id']

    def add_warning(self, content: str, title: str = None) -> str:
        """Add warning callout."""
        callout = self.note_renderer.create_quarto_callout(content, "warning", title)
        self.add_content(f"\n\n{callout['markdown']}\n\n")
        return callout['ref_id']

    def add_error(self, content: str, title: str = None) -> str:
        """Add error callout."""
        callout = self.note_renderer.create_quarto_callout(content, "caution", title)
        self.add_content(f"\n\n{callout['markdown']}\n\n")
        return callout['ref_id']

    def add_success(self, content: str, title: str = None) -> str:
        """Add success callout."""
        callout = self.note_renderer.create_quarto_callout(content, "success", title)
        self.add_content(f"\n\n{callout['markdown']}\n\n")
        return callout['ref_id']

    def add_caution(self, content: str, title: str = None) -> str:
        """Add caution callout with yellow styling."""
        callout = self.note_renderer.create_quarto_callout(content, "caution", title)
        self.add_content(f"\n\n{callout['markdown']}\n\n")
        return callout['ref_id']

    def add_important(self, content: str, title: str = None) -> str:
        """Add important callout with red styling."""
        callout = self.note_renderer.create_quarto_callout(content, "important", title)
        self.add_content(f"\n\n{callout['markdown']}\n\n")
        return callout['ref_id']

    # Equations
    def add_equation(self, latex_code: str, caption: str = None, label: str = None) -> str:
        """Add numbered block equation."""
        formatted = self.equation_processor.format_equation(latex_code, label, caption)
        equation_markdown = self.equation_processor.get_equation_markdown(formatted)
        self.add_content(equation_markdown)
        return formatted['label']

    def add_equation_in_line(self, latex_code: str) -> None:
        """Add inline equation (not numbered)."""
        inline_equation = self.equation_processor.format_inline_equation(latex_code)
        self.add_inline_content(inline_equation)

    def add_equation_block(self, equations: List[str], caption: str = None,
                          label: str = None, align: bool = True) -> str:
        """Add block of multiple aligned equations."""
        formatted = self.equation_processor.format_equation_block(equations, label, caption, align)
        equation_markdown = self.equation_processor.get_equation_markdown(formatted)
        self.add_content(equation_markdown)
        return formatted['label']

    def add_reference(self, ref_type: str, ref_id: str, custom_text: str = None) -> str:
        """Add cross-reference to figure, table, equation, or note."""
        from ePy_docs.references.references import format_cross_reference
        
        if ref_type == 'note':
            reference = self.note_renderer.create_cross_reference(ref_id, custom_text)
        else:
            reference = format_cross_reference(ref_type, ref_id, custom_text)
        
        self.add_content(reference)
        return reference

    def add_citation(self, citation_key: str, page: str = None) -> str:
        """Add inline citation."""
        from ePy_docs.references.references import format_citation
        
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
                qmd: bool = False, tex: bool = False, citation_style: str = None,
                output_filename: str = None) -> None:
        """Generate report in requested formats.
        
        Args:
            markdown: Generate .md file
            html: Generate .html file
            pdf: Generate .pdf file
            qmd: Generate .qmd file (Quarto Markdown)
            tex: Generate .tex file (LaTeX)
            citation_style: Citation style to use
            output_filename: Custom filename for output files (without extension)
        """
        from ePy_docs.formats.generator import generate_documents
        
        # Prepare content
        content = ''.join(self.content_buffer)
        
        # Generate documents using the dedicated generator module
        generate_documents(
            content=content,
            file_path=self.file_path,
            markdown=markdown,
            html=html,
            pdf=pdf,
            qmd=qmd,
            tex=tex,
            citation_style=citation_style,
            output_filename=output_filename
        )

    # Project-specific Content
    def add_responsability_page(self) -> str:
        """Add responsibility page from project configuration."""
        from ePy_docs.project.responsible import add_responsibility_text
        add_responsibility_text(self)
        return "Responsibility page added"

    def add_copyright_footer(self) -> str:
        """Add copyright footer from project configuration."""
        from ePy_docs.project.copyright import create_copyright_page
        project_config = get_full_project_config()
        create_copyright_page(project_config, self)

