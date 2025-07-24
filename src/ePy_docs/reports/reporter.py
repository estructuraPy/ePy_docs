import os
import tempfile
import shutil
from typing import Dict, List, Any, Optional, Union, Tuple

import pandas as pd
import matplotlib.pyplot as plt
from pydantic import Field

from ePy_docs.core.base import WriteFiles
from ePy_docs.components.tables import create_table_image, create_split_table_images
from ePy_docs.components.images import ImageProcessor
from ePy_docs.components.notes import NoteRenderer
from ePy_docs.components.equations import EquationProcessor
from ePy_docs.styler.setup import get_full_project_config


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
    equation_counter: int = Field(default=0)
    output_dir: str = Field(default="")
    show_in_notebook: bool = Field(default=True, description="Whether to display images in Jupyter notebooks")
    note_renderer: NoteRenderer = Field(default_factory=NoteRenderer)
    equation_processor: EquationProcessor = Field(default_factory=lambda: EquationProcessor(equation_counter=0))

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
        self.add_content(f"\n# {text}\n\n")

    def add_h2(self, text: str) -> None:
        """Add H2 header."""
        self.add_content(f"\n## {text}\n\n")

    def add_h3(self, text: str) -> None:
        """Add H3 header."""
        self.add_content(f"\n### {text}\n\n")

    # Text and lists
    def add_text(self, content: str) -> None:
        """Add text content."""
        self.add_content(f"{content}\n\n")

    def add_list(self, items: List[str], ordered: bool = False) -> None:
        """Add bulleted or numbered list."""
        list_items = []
        for i, item in enumerate(items, 1):
            if ordered:
                list_items.append(f"{i}. {item}")
            else:
                list_items.append(f"- {item}")
        self.add_content("\n".join(list_items) + "\n\n")

    # Tables
    def add_table(self, df: pd.DataFrame, title: str = None,
                  hide_columns: Union[str, List[str]] = None,
                  filter_by: Union[Tuple, List[Tuple]] = None,
                  sort_by: Union[str, Tuple, List] = None,
                  max_rows_per_table: Optional[Union[int, List[int]]] = None,
                  palette_name: Optional[str] = None,
                  n_rows: Optional[Union[int, List[int]]] = None) -> None:
        """Add simple table to report.
        
        Args:
            palette_name: Optional color palette for table (not used in simple tables, kept for API consistency)
            n_rows: Take only the first N rows from the DataFrame (subset)
        """
        # Load table configuration using our unified system
        from ePy_docs.components.tables import _load_table_config
        tables_config = _load_table_config()
        
        tables_dir = os.path.join(self.output_dir, "tables")
        os.makedirs(tables_dir, exist_ok=True)

        # Handle n_rows as subset (take first N rows) vs max_rows_per_table (split into multiple tables)
        if n_rows is not None:
            # n_rows means take only first N rows (subset)
            df = df.head(n_rows)
        
        effective_max_rows = max_rows_per_table

        # Handle max_rows_per_table as list or int 
        if effective_max_rows is not None:
            if isinstance(effective_max_rows, list):
                # For lists, check if any splitting is needed by comparing total rows
                # against the sum of all specified chunk sizes
                total_specified_rows = sum(effective_max_rows)
                needs_splitting = len(df) > min(effective_max_rows) or len(effective_max_rows) > 1
                max_rows_for_check = effective_max_rows  # Pass the full list for splitting
            else:
                needs_splitting = len(df) > effective_max_rows
                max_rows_for_check = effective_max_rows
        else:
            needs_splitting = False
            max_rows_for_check = None

        if needs_splitting:
            img_paths = create_split_table_images(
                df=df, output_dir=tables_dir, base_table_number=self.table_counter + 1,
                title=title, dpi=tables_config['display']['dpi'], hide_columns=hide_columns,
                filter_by=filter_by, sort_by=sort_by,
                max_rows_per_table=max_rows_for_check
            )
            # Increment counter by the number of tables created
            self.table_counter += len(img_paths)
        else:
            img_path = create_table_image(
                df=df, output_dir=tables_dir, table_number=self.table_counter + 1,
                title=title, dpi=tables_config['display']['dpi'], hide_columns=hide_columns,
                filter_by=filter_by, sort_by=sort_by
            )
            img_paths = [img_path]
            self.table_counter += 1

        # Load table configuration for fig-width - no hardcoded values
        from ePy_docs.components.tables import _load_table_config
        table_config = _load_table_config()
        display_config = table_config['display']
        
        # Use HTML-specific width for better sizing in HTML output when html_responsive is enabled
        if display_config['html_responsive']:
            fig_width = display_config['max_width_inches_html']
        else:
            fig_width = display_config['max_width_inches']

        for i, img_path in enumerate(img_paths):
            rel_path = ImageProcessor.get_relative_path(img_path, self.output_dir)
            
            # Each split table gets its own sequential number
            table_number = self.table_counter - len(img_paths) + i + 1
            table_id = f"tbl-{table_number}"
            
            # Apply proper title formatting for split tables
            if len(img_paths) > 1:
                # Multiple tables - use multi_table_title_format
                if title:
                    multi_format = table_config['pagination']['multi_table_title_format']
                    table_caption = multi_format.format(
                        title=title, 
                        part=i + 1, 
                        total=len(img_paths)
                    )
                else:
                    no_title_format = table_config['pagination']['multi_table_no_title_format']
                    table_caption = no_title_format.format(
                        part=i + 1, 
                        total=len(img_paths)
                    )
            else:
                # Single table - use single_table_title_format
                if title:
                    single_format = table_config['pagination']['single_table_title_format']
                    table_caption = single_format.format(title=title)
                else:
                    table_caption = f"Table {table_number}"

            # Always add caption since table_caption is always generated  
            self.add_content(f"\n\n![{table_caption}]({rel_path}){{#{table_id} fig-width={fig_width}}}\n\n")
            
            # Display image in notebook if available
            self._display_in_notebook(img_path)

        # Don't return paths to avoid printing them in notebooks/console
        return None

    def add_colored_table(self, df: pd.DataFrame, title: str = None,
                          highlight_columns: Optional[List[str]] = None,
                          hide_columns: Union[str, List[str]] = None,
                          filter_by: Union[Tuple, List[Tuple]] = None,
                          sort_by: Union[str, Tuple, List] = None,
                          max_rows_per_table: Optional[Union[int, List[int]]] = None,
                          palette_name: Optional[str] = None,
                          n_rows: Optional[Union[int, List[int]]] = None) -> None:
        """Add colored table to report.
        
        Args:
            n_rows: Take only the first N rows from the DataFrame (subset)
        """
        # Load table configuration using our unified system
        from ePy_docs.components.tables import _load_table_config
        tables_config = _load_table_config()
        
        tables_dir = os.path.join(self.output_dir, "tables")
        os.makedirs(tables_dir, exist_ok=True)

        # Use provided palette_name or fall back to configuration
        table_palette = palette_name if palette_name is not None else tables_config['palette_name']

        # Handle n_rows as subset (take first N rows) vs max_rows_per_table (split into multiple tables)
        if n_rows is not None:
            # n_rows means take only first N rows (subset)
            df = df.head(n_rows)
        
        effective_max_rows = max_rows_per_table

        # Handle max_rows_per_table as list or int
        if effective_max_rows is not None:
            if isinstance(effective_max_rows, list):
                # For lists, check if any splitting is needed by comparing total rows
                # against the sum of all specified chunk sizes
                total_specified_rows = sum(effective_max_rows)
                needs_splitting = len(df) > min(effective_max_rows) or len(effective_max_rows) > 1
                max_rows_for_check = effective_max_rows  # Pass the full list for splitting
            else:
                needs_splitting = len(df) > effective_max_rows
                max_rows_for_check = effective_max_rows
        else:
            needs_splitting = False
            max_rows_for_check = None

        if needs_splitting:
            img_paths = create_split_table_images(
                df=df, output_dir=tables_dir, base_table_number=self.table_counter + 1,
                title=title, highlight_columns=highlight_columns,
                palette_name=table_palette, dpi=tables_config['display']['dpi'],
                hide_columns=hide_columns, filter_by=filter_by, sort_by=sort_by,
                max_rows_per_table=max_rows_for_check
            )
            # Increment counter by the number of tables created
            self.table_counter += len(img_paths)
        else:
            img_path = create_table_image(
                df=df, output_dir=tables_dir, table_number=self.table_counter + 1,
                title=title, highlight_columns=highlight_columns,
                palette_name=table_palette, dpi=tables_config['display']['dpi'],
                hide_columns=hide_columns, filter_by=filter_by, sort_by=sort_by
            )
            img_paths = [img_path]
            self.table_counter += 1

        # Load table configuration for fig-width - no hardcoded values
        from ePy_docs.components.tables import _load_table_config
        table_config = _load_table_config()
        display_config = table_config['display']
        
        # Use HTML-specific width for better sizing in HTML output when html_responsive is enabled
        if display_config['html_responsive']:
            fig_width = display_config['max_width_inches_html']
        else:
            fig_width = display_config['max_width_inches']

        for i, img_path in enumerate(img_paths):
            rel_path = ImageProcessor.get_relative_path(img_path, self.output_dir)
            
            # Each split table gets its own sequential number
            table_number = self.table_counter - len(img_paths) + i + 1
            table_id = f"tbl-{table_number}"
            
            # Apply proper title formatting for split tables
            if len(img_paths) > 1:
                # Multiple tables - use multi_table_title_format
                if title:
                    multi_format = table_config['pagination']['multi_table_title_format']
                    table_caption = multi_format.format(
                        title=title, 
                        part=i + 1, 
                        total=len(img_paths)
                    )
                else:
                    no_title_format = table_config['pagination']['multi_table_no_title_format']
                    table_caption = no_title_format.format(
                        part=i + 1, 
                        total=len(img_paths)
                    )
            else:
                # Single table - use single_table_title_format
                if title:
                    single_format = table_config['pagination']['single_table_title_format']
                    table_caption = single_format.format(title=title)
                else:
                    table_caption = f"Table {table_number}"

            # Always add caption since table_caption is always generated
            self.add_content(f"\n\n![{table_caption}]({rel_path}){{#{table_id} fig-width={fig_width}}}\n\n")
            
            # Display image in notebook if available
            self._display_in_notebook(img_path)

        # Don't return paths to avoid printing them in notebooks/console
        return None

    # Figures and Images
    def add_plot(self, fig: plt.Figure, title: str = None, caption: str = None) -> str:
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
        if final_caption:
            self.add_content(f"\n\n![]({rel_path}){{#{figure_id}}}\n\n: {final_caption}\n\n")
        else:
            self.add_content(f"\n\n![]({rel_path}){{#{figure_id}}}\n\n")
        
        return img_path

    def add_image(self, path: str, caption: str = None, width: str = None,
                  alt_text: str = None, align: str = None) -> str:
        """Add external image to report."""
        self.figure_counter += 1
        
        dest_path = ImageProcessor.organize_image(path, self.output_dir, "figures")
        rel_path = ImageProcessor.get_relative_path(dest_path, self.output_dir)
        
        figure_id = f"fig-{self.figure_counter}"
        img_alt = alt_text or caption or f"Figure {self.figure_counter}"
        
        # Build image markdown with attributes
        img_markdown = f"![{img_alt}]({rel_path})"
        attributes = []
        if width:
            attributes.append(f'width="{width}"')
        if align:
            attributes.append(f'fig-align="{align}"')
        attributes.append(f'#{figure_id}')
        
        img_markdown += " {" + " ".join(attributes) + "}"
        self.add_content(f"\n\n{img_markdown}")
        
        if caption:
            self.add_content(f"\n\n: {caption}")
        
        self.add_content("\n\n")
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
        if ref_type == 'note':
            reference = self.note_renderer.create_cross_reference(ref_id, custom_text)
        elif ref_type in ['fig', 'tbl', 'eq']:
            if custom_text:
                reference = f"[{custom_text}](#{ref_id})"
            else:
                reference = f"@{ref_id}"
        else:
            raise ValueError(f"Invalid reference type: {ref_type}")
        
        self.add_content(reference)
        return reference

    def add_citation(self, citation_key: str, page: str = None) -> str:
        """Add inline citation."""
        if page:
            citation = f"[@{citation_key}, p. {page}]"
        else:
            citation = f"[@{citation_key}]"
        
        self.add_inline_content(citation)
        return citation

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
        if not any([markdown, html, pdf, qmd, tex]):
            raise ValueError("No output formats requested")

        project_config = get_full_project_config()
        if not citation_style:
            citation_style = project_config['styling']['citations']['default_style']
        
        # Sync reference files based on citation style
        from ePy_docs.styler.setup import sync_ref
        sync_ref(citation_style)

        # Create output directory
        directory = os.path.dirname(self.file_path)
        if directory:
            os.makedirs(directory, exist_ok=True)

        # Determine base filename
        if output_filename:
            # Use provided custom filename
            base_filename = os.path.join(directory, output_filename)
        else:
            # Try to get filename from setup configuration
            try:
                from ePy_docs.project.setup import DirectoryConfig
                setup_config = DirectoryConfig()
                # Get the report filename without extension from the report_md path
                report_path = setup_config.report_md
                if report_path:
                    # Extract just the filename without extension
                    report_filename = os.path.splitext(os.path.basename(report_path))[0]
                    base_filename = os.path.join(directory, report_filename)
                else:
                    # Fallback to original file path behavior
                    base_filename = os.path.splitext(self.file_path)[0]
            except:
                # Fallback to original file path behavior
                base_filename = os.path.splitext(self.file_path)[0]
        
        # Prepare content
        content = ''.join(self.content_buffer)
        
        # Generate QMD file if requested
        if qmd:
            from ePy_docs.formats.quarto import QuartoConverter
            
            project_info = project_config['project']
            title = project_info['name']  # Use 'name' instead of 'title'
            
            # Handle consultants array - use first consultant as author
            consultants = project_config['consultants']
            author = consultants[0]['name']

            converter = QuartoConverter()
            qmd_path = converter.markdown_to_qmd(
                content, title=title, author=author,
                output_file=f"{base_filename}.qmd", citation_style=citation_style
            )
        
        # Generate TEX file if requested - create it BEFORE conversions to avoid cleanup
        tex_path = None
        if tex:
            tex_path = f"{base_filename}.tex"
            with open(tex_path, 'w', encoding='utf-8') as f:
                f.write(content)
        
        # Generate markdown file if requested or needed for conversions
        if markdown or html or pdf:
            markdown_path = f"{base_filename}.md"
            with open(markdown_path, 'w', encoding='utf-8') as f:
                f.write(content)
        else:
            markdown_path = None

        # Generate other formats if requested
        if html or pdf:
            from ePy_docs.formats.quarto import QuartoConverter
            
            project_info = project_config['project']
            title = project_info['name']  # Use 'name' instead of 'title'
            
            # Handle consultants array - use first consultant as author
            consultants = project_config['consultants']
            author = consultants[0]['name']

            converter = QuartoConverter()
            
            # If QMD or TEX was requested, don't clean temp files to preserve our files
            clean_temp = not (qmd or tex)

            if html:
                converter.convert_markdown_to_html(
                    markdown_content=markdown_path, title=title, author=author,
                    output_file=f"{base_filename}.html", citation_style=citation_style,
                    clean_temp=clean_temp
                )

            if pdf:
                converter.convert_markdown_to_pdf(
                    markdown_content=markdown_path, title=title, author=author,
                    output_file=f"{base_filename}.pdf", citation_style=citation_style,
                    clean_temp=clean_temp
                )

        # Remove temporary markdown file if not explicitly requested
        if not markdown and (html or pdf) and markdown_path and os.path.exists(markdown_path):
            os.remove(markdown_path)
        
        # Final verification and recreation for requested files
        if qmd:
            qmd_path = f"{base_filename}.qmd"
            if not os.path.exists(qmd_path):
                from ePy_docs.formats.quarto import QuartoConverter
                
                project_info = project_config['project']
                title = project_info['name']  # Use 'name' instead of 'title'
                
                # Handle consultants array - use first consultant as author
                consultants = project_config['consultants']
                author = consultants[0]['name']

                converter = QuartoConverter()
                qmd_path = converter.markdown_to_qmd(
                    content, title=title, author=author,
                    output_file=f"{base_filename}.qmd", citation_style=citation_style
                )
        
        if tex:
            tex_path = f"{base_filename}.tex"
            if not os.path.exists(tex_path):
                with open(tex_path, 'w', encoding='utf-8') as f:
                    f.write(content)
        
        # Final cleanup: remove any Quarto-generated _files directories
        self._cleanup_quarto_files_directories(base_filename)

    def _cleanup_quarto_files_directories(self, base_filename: str) -> None:
        """Clean up any Quarto-generated _files directories.
        
        Args:
            base_filename: Base filename (without extension) used for the report
        """
        try:
            # Check for various possible _files directories
            directory = os.path.dirname(base_filename) if os.path.dirname(base_filename) else "."
            basename_only = os.path.basename(base_filename)
            
            # Possible patterns for _files directories
            files_patterns = [
                f"{basename_only}_files",
                f"{os.path.basename(self.file_path).split('.')[0]}_files"
            ]
            
            for pattern in files_patterns:
                files_dir = os.path.join(directory, pattern)
                if os.path.exists(files_dir) and os.path.isdir(files_dir):
                    shutil.rmtree(files_dir)
        except Exception:
            # Silent cleanup - don't fail if we can't clean up
            pass

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

    def _display_in_notebook(self, img_path: str) -> None:
        """Display image in Jupyter notebook if available."""
        if not self.show_in_notebook:
            return
        
        try:
            from IPython.display import Image, display
            from IPython import get_ipython
            from ePy_docs.core.content import _load_cached_config
            
            if get_ipython() is not None:
                if os.path.exists(img_path):
                    units_config = _load_cached_config('units')
                    image_width = units_config['display']['formatting']['image_display_width']
                    display(Image(img_path, width=image_width))
        except (ImportError, Exception):
            # Silently skip display if not in Jupyter or any other error
            pass
        return "Copyright footer added"
