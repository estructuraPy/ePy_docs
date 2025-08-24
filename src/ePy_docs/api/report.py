import os
from typing import Dict, List, Any, Optional, Union, Tuple

import pandas as pd
import matplotlib.pyplot as plt
from pydantic import Field

from ePy_docs.core.base import WriteFiles
from ePy_docs.components.tables import create_table_image, create_split_table_images
from ePy_docs.components.images import ImageProcessor, display_in_notebook
from ePy_docs.components.notes import NoteRenderer
from ePy_docs.components.equations import EquationProcessor
from ePy_docs.components.text import _get_layout_config
from ePy_docs.components.page import get_layout_name
from ePy_docs.core.setup import load_setup_config, get_output_directories
from ePy_docs.components.project_info import get_project_config_data


class ReportWriter(WriteFiles):
    """Clean writer for technical reports - all configuration from JSON files.
    
    Automatically constructs file paths from setup.json and project_info.json.
    No hardcoded values, no fallbacks, no verbose output.
    Configuration must exist in components/*.json files.
    """
    
    model_config = {"arbitrary_types_allowed": True}

    table_counter: int = Field(default=0)
    figure_counter: int = Field(default=0)
    note_counter: int = Field(default=0)
    output_dir: str = Field(default="")
    show_in_notebook: bool = Field(default=True)
    note_renderer: NoteRenderer = Field(default_factory=NoteRenderer)
    equation_processor: EquationProcessor = Field(default_factory=EquationProcessor)

    def __init__(self, sync_files: bool = True, **data):
        """Initialize ReportWriter using JSON configurations only.
        
        Args:
            sync_files: Whether to use synchronized configuration files
        """
        # Get configurations from JSON files
        output_dirs = get_output_directories(sync_json=sync_files)
        project_config = get_project_config_data(sync_json=sync_files)
        
        # Construct file_path automatically from configurations
        report_name = project_config['project']['report']
        report_dir = output_dirs['report']
        auto_file_path = os.path.join(report_dir, f"{report_name}.md")
        
        # Use auto-generated file_path if not provided
        if 'file_path' not in data:
            data['file_path'] = auto_file_path
            
        super().__init__(**data)
        self.file_path = os.path.abspath(self.file_path)
        
        # Use report directory from setup.json
        self.output_dir = report_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def _get_layout_name(self) -> str:
        """Get current layout name from report.json configuration."""
        return get_layout_name()
        if not layout_name:
            raise ValueError("Layout name not configured in report.json")
        return layout_name

    def _get_text_config(self) -> Dict[str, Any]:
        """Get text configuration for current layout - must exist in text.json."""
        layout_name = self._get_layout_name()
        text_config = _get_layout_config(layout_name)
        if not text_config:
            raise ValueError(f"Text configuration not found for layout '{layout_name}' in text.json")
        return text_config


    # Headers - Configuration from text.json only
    def add_h1(self, text: str) -> None:
        """Add H1 header using text.json configuration."""
        from ePy_docs.components.text import format_header_h1
        
        layout_name = self._get_layout_name()
        formatted_header = format_header_h1(text, layout_name)
        self.add_content(formatted_header)

    def add_h2(self, text: str) -> None:
        """Add H2 header using text.json configuration."""
        from ePy_docs.components.text import format_header_h2
        
        layout_name = self._get_layout_name()
        formatted_header = format_header_h2(text, layout_name)
        self.add_content(formatted_header)

    def add_h3(self, text: str) -> None:
        """Add H3 header using text.json configuration."""
        from ePy_docs.components.text import format_header_h3
        
        layout_name = self._get_layout_name()
        formatted_header = format_header_h3(text, layout_name)
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

    # Tables - Configuration from tables.json only
    def add_table(self, df: pd.DataFrame, title: str = None,
                  hide_columns: Union[str, List[str]] = None,
                  filter_by: Union[Tuple, List[Tuple]] = None,
                  sort_by: Union[str, Tuple, List] = None,
                  max_rows_per_table: Optional[Union[int, List[int]]] = None,
                  palette_name: Optional[str] = None,
                  n_rows: Optional[Union[int, List[int]]] = None,
                  source: Optional[str] = None) -> None:
        """Add table to report using tables.json configuration."""
        from ePy_docs.components.tables import add_table_to_content
        
        # Pass None as output_dir to use dynamic configuration
        markdown_list, self.table_counter = add_table_to_content(
            df=df, output_dir=None, table_counter=self.table_counter,
            title=title, hide_columns=hide_columns, filter_by=filter_by,
            sort_by=sort_by, max_rows_per_table=max_rows_per_table, n_rows=n_rows,
            source=source
        )
        
        for table_markdown, img_path in markdown_list:
            self.add_content(table_markdown)

    def add_colored_table(self, df: pd.DataFrame, title: str = None,
                          highlight_columns: Optional[List[str]] = None,
                          hide_columns: Union[str, List[str]] = None,
                          filter_by: Union[Tuple, List[Tuple]] = None,
                          sort_by: Union[str, Tuple, List] = None,
                          max_rows_per_table: Optional[Union[int, List[int]]] = None,
                          palette_name: Optional[str] = None,
                          n_rows: Optional[Union[int, List[int]]] = None,
                          source: Optional[str] = None) -> None:
        """Add colored table to report using tables.json and colors.json configuration."""
        from ePy_docs.components.tables import add_colored_table_to_content
        
        # Pass None as output_dir to use dynamic configuration
        markdown_list, self.table_counter = add_colored_table_to_content(
            df=df, output_dir=None, table_counter=self.table_counter,
            title=title, highlight_columns=highlight_columns, hide_columns=hide_columns,
            filter_by=filter_by, sort_by=sort_by, max_rows_per_table=max_rows_per_table,
            palette_name=palette_name, n_rows=n_rows, source=source
        )
        
        for table_markdown, img_path in markdown_list:
            self.add_content(table_markdown)
            display_in_notebook(img_path, self.show_in_notebook)

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
        
        fig.savefig(img_path, bbox_inches='tight', dpi=figures_config['dpi'], 
                   facecolor='white', edgecolor='none')
        
        rel_path = ImageProcessor.get_quarto_relative_path(img_path, self.output_dir)
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
        """Generate report in requested formats.
        
        Citation style is automatically determined from the layout configured in page.json.
        
        Args:
            markdown: Generate .md file
            html: Generate .html file
            pdf: Generate .pdf file
            qmd: Generate .qmd file (Quarto Markdown)
            tex: Generate .tex file (LaTeX)
            output_filename: Custom filename for output files (without extension)
            sync_json: Whether to read configuration from local JSON files
        """
        from ePy_docs.core.generator import generate_documents
        
        # Prepare content
        content = ''.join(self.content_buffer)
        
        # Generate documents using the dedicated generator module
        # Citation style is determined automatically from layout
        generate_documents(
            content=content,
            file_path=self.file_path,
            markdown=markdown,
            html=html,
            pdf=pdf,
            qmd=qmd,
            tex=tex,
            output_filename=output_filename,
            output_dir=self.output_dir
        )

    # Project-specific Content
    def add_responsability_page(self) -> str:
        """Add responsibility page from project configuration."""
        from ePy_docs.components.project_info import add_responsibility_text
        add_responsibility_text(self)
        return "Responsibility page added"

    def add_copyright_footer(self) -> str:
        """Add copyright footer from project.json configuration."""
        from ePy_docs.components.project_info import create_copyright_page
        from ePy_docs.core.setup import _load_cached_config
        
        # Load project configuration directly from project.json
        project_config = _load_cached_config('project')
        if not project_config:
            raise ValueError("Project configuration not found in project.json - required for copyright footer")
        
        create_copyright_page(project_config, self)

