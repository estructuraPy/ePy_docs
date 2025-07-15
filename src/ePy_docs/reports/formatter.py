import os
import tempfile
import datetime
from typing import Dict, List, Any, Optional, Union, Tuple

import pandas as pd
import matplotlib.pyplot as plt
from pydantic import BaseModel, Field

from ePy_docs.core.base import WriteFiles
from ePy_docs.core.content import ContentProcessor
from ePy_docs.core.text import TextFormatter
from ePy_docs.components.tables import create_table_image, create_split_table_images
from ePy_docs.components.images import ImageProcessor
from ePy_docs.components.notes import NoteRenderer
from ePy_docs.components.equations import EquationProcessor
from ePy_docs.styler.colors import get_color, _load_cached_colors
from ePy_docs.styler.setup import get_config_value, get_project_config
from tqdm import tqdm


class ReportFormatter(WriteFiles):
    """Advanced formatter for technical and academic reports.

    Args:
        file_path: Path to the output file.
        content_buffer: List of content strings to be written to the output file.
        table_counter: Counter for table numbering.
        figure_counter: Counter for figure numbering.
        note_counter: Counter for note numbering.
        equation_counter: Counter for equation numbering.
        temp_dir: Temporary directory for storing intermediate files.
        generated_images: List of paths to generated images.
        output_dir: Output directory for generated files.
        show_in_notebook: Whether to display images in Jupyter notebooks.
        note_renderer: Note renderer instance.
        equation_processor: Equation processor instance.

    Returns:
        None

    Assumptions:
        - All dependencies are installed.
        - The file paths are valid.
    """

    model_config = {"arbitrary_types_allowed": True}

    table_counter: int = Field(default=0, description="Counter for table numbering")
    figure_counter: int = Field(default=0, description="Counter for figure numbering")
    note_counter: int = Field(default=0, description="Counter for note numbering")
    equation_counter: int = Field(default=0, description="Counter for equation numbering")
    temp_dir: str = Field(default_factory=lambda: os.path.join(tempfile.gettempdir(), 'epy_reports'))
    generated_images: List[str] = Field(default_factory=list)
    output_dir: str = Field(default="", description="Output directory for generated files")
    show_in_notebook: bool = Field(default=True, description="Whether to display images in Jupyter notebooks")
    note_renderer: NoteRenderer = Field(default_factory=NoteRenderer, description="Note renderer instance")
    equation_processor: EquationProcessor = Field(default_factory=EquationProcessor, description="Equation processor instance")

    def __init__(self, **data):
        """Initialize ReportFormatter with proper directory setup."""
        super().__init__(**data)
        self.file_path = os.path.abspath(self.file_path)

        if not self.output_dir:
            self.output_dir = os.path.dirname(self.file_path)
        else:
            self.output_dir = os.path.abspath(self.output_dir)

        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.temp_dir, exist_ok=True)

    def add_table(self, df: pd.DataFrame, title: str = None,
                  dpi: int = 300, hide_columns: Union[str, List[str]] = None,
                  filter_by: Union[Tuple, List[Tuple]] = None,
                  sort_by: Union[str, Tuple, List] = None,
                  split_large_tables: bool = True,
                  max_rows_per_table: Optional[int] = None,
                  n_rows: Optional[int] = None,
                  label: str = None, caption: str = None) -> List[str]:
        """Generate table using components module.

        Args:
            df: Pandas DataFrame to be converted into a table.
            title: Title of the table.
            dpi: DPI of the generated image.
            hide_columns: Columns to hide in the table.
            filter_by: Filter rows based on conditions.
            sort_by: Sort rows based on columns.
            split_large_tables: Whether to split large tables into multiple images.
            max_rows_per_table: Maximum number of rows per table when splitting.
            n_rows: Number of rows to display.
            label: Label for the table.
            caption: Caption for the table.

        Returns:
            A list of image paths representing the generated table(s).

        Assumptions:
            - The input DataFrame is valid.
            - The specified columns exist in the DataFrame.
        """
        tables_dir = os.path.join(self.output_dir, "tables")
        os.makedirs(tables_dir, exist_ok=True)

        if split_large_tables:
            img_paths = create_split_table_images(
                df=df, output_dir=tables_dir, base_table_number=self.table_counter + 1,
                title=title, dpi=dpi, hide_columns=hide_columns,
                filter_by=filter_by, sort_by=sort_by,
                max_rows_per_table=max_rows_per_table, n_rows=n_rows
            )
            self.table_counter += 1
        else:
            img_path = create_table_image(
                df=df, output_dir=tables_dir, table_number=self.table_counter + 1,
                title=title, dpi=dpi, hide_columns=hide_columns,
                filter_by=filter_by, sort_by=sort_by, n_rows=n_rows
            )
            img_paths = [img_path]
            self.table_counter += 1

        # Algo nuevo: Add progress bar for table processing
        for i, img_path in enumerate(tqdm(img_paths, desc="Adding Tables")):
            rel_path = ImageProcessor.get_relative_path(img_path, self.output_dir)

            # Create table ID and caption
            if len(img_paths) > 1:
                table_id = f"tbl-{label}-{i+1}" if label else f"tbl-{self.table_counter:03d}-{i+1}"
                table_caption = f"{title} (Part {i+1}/{len(img_paths)})" if title else f"Table {self.table_counter} (Part {i+1}/{len(img_paths)})"
            else:
                table_id = f"tbl-{label}" if label else f"tbl-{self.table_counter:03d}"
                table_caption = caption if caption else title

            # Use Quarto table format
            if table_caption:
                self.add_content(f"\n\n![]({rel_path}){{#{table_id}}}\n\n: {table_caption}\n\n")
            else:
                self.add_content(f"\n\n![]({rel_path}){{#{table_id}}}\n\n")

            self.generated_images.append(img_path)
            if self.show_in_notebook:
                self._display_in_notebook(img_path)

        return img_paths

    def add_colored_table(self, df: pd.DataFrame, title: str = None,
                          palette_name: str = 'YlOrRd',
                          highlight_columns: Optional[List[str]] = None,
                          **kwargs) -> List[str]:
        """Generate colored table.

        Args:
            df: Pandas DataFrame to be converted into a table.
            title: Title of the table.
            palette_name: Name of the color palette to use.
            highlight_columns: Columns to highlight with colors.
            **kwargs: Additional keyword arguments to pass to the table creation function.

        Returns:
            A list of image paths representing the generated table(s).

        Assumptions:
            - The input DataFrame is valid.
            - The specified columns exist in the DataFrame.
        """
        tables_dir = os.path.join(self.output_dir, "tables")
        os.makedirs(tables_dir, exist_ok=True)

        # Extract parameters that need special handling
        split_large_tables = kwargs.get('split_large_tables', True)

        if split_large_tables:
            img_paths = create_split_table_images(
                df=df,
                output_dir=tables_dir,
                base_table_number=self.table_counter + 1,
                title=title,
                highlight_columns=highlight_columns,
                palette_name=palette_name,
                **kwargs
            )
            self.table_counter += 1
        else:
            img_path = create_table_image(
                df=df,
                output_dir=tables_dir,
                table_number=self.table_counter + 1,
                title=title,
                highlight_columns=highlight_columns,
                palette_name=palette_name,
                **kwargs
            )
            img_paths = [img_path]
            self.table_counter += 1

        # Algo nuevo: Add progress bar for colored table processing
        for i, img_path in enumerate(tqdm(img_paths, desc="Adding Colored Tables")):
            # Use ImageProcessor for consistent path handling
            rel_path = ImageProcessor.get_relative_path(img_path, self.output_dir)

            # Create table ID and caption using same system as add_table()
            if len(img_paths) > 1:
                table_id = f"tbl-{self.table_counter:03d}-{i+1}"
                table_caption = f"{title} (Part {i+1}/{len(img_paths)})" if title else f"Table {self.table_counter} (Part {i+1}/{len(img_paths)})"
            else:
                table_id = f"tbl-{self.table_counter:03d}"
                table_caption = title if title else f"Table {self.table_counter}"

            # Use Quarto table format
            if table_caption:
                self.add_content(f"\n\n![]({rel_path}){{#{table_id}}}\n\n: {table_caption}\n\n")
            else:
                self.add_content(f"\n\n![]({rel_path}){{#{table_id}}}\n\n")

            self.generated_images.append(img_path)
            if self.show_in_notebook:
                self._display_in_notebook(img_path)

        return img_paths

    def add_plot(self, title: str = None, filename: str = None, fig: plt.Figure = None, caption: str = None,
                 width_inches: float = None, height_inches: float = None, dpi: int = 300) -> str:
        """Add plot to the report with proper numbering.

        Args:
            title: Title of the plot.
            filename: Filename for the plot image.
            fig: Matplotlib figure object.
            caption: Caption for the plot.
            width_inches: Width of the plot in inches.
            height_inches: Height of the plot in inches.
            dpi: DPI of the plot image.

        Returns:
            The path to the saved image.

        Assumptions:
            - Matplotlib is installed and configured correctly.
            - If a figure object is not provided, the current figure is used.
        """
        if fig is None:
            fig = plt.gcf()

        if width_inches or height_inches:
            width_inches = width_inches or height_inches  # Use height if width is missing
            height_inches = height_inches or width_inches  # Use width if height is missing
            fig.set_size_inches(width_inches, height_inches)

        self.figure_counter += 1

        if filename is None:
            img_filename = f"figure_{self.figure_counter:03d}.png"
        else:
            img_filename = filename
            if not img_filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                img_filename += '.png'

        figures_dir = os.path.join(self.output_dir, "figures")
        os.makedirs(figures_dir, exist_ok=True)
        img_path = os.path.join(figures_dir, img_filename)

        # Add title and caption to figure if provided
        if title or caption:
            fig.subplots_adjust(bottom=0.15)  # Adjust bottom to make space for the title
            if title:
                try:
                    ax = fig.gca()
                    ax.text(0.01, 0.99, title, transform=ax.transAxes,
                           fontsize=14, fontweight='bold', va='top', ha='left')
                except Exception:
                    pass  # Fail silently

        fig.savefig(img_path, bbox_inches='tight', dpi=dpi, facecolor='white', edgecolor='none')

        if self.show_in_notebook:
            self._display_in_notebook(img_path)

        # Add to markdown
        rel_path = ImageProcessor.get_relative_path(img_path, self.output_dir)
        figure_id = f"fig-{self.figure_counter:03d}"

        if caption:
            self.add_content(f"\n\n![]({rel_path}){{#{figure_id}}}\n\n: {caption}\n\n")
        else:
            self.add_content(f"\n\n![]({rel_path}){{#{figure_id}}}\n\n")

        self.generated_images.append(img_path)
        return img_path

    def add_image(self, path: str, caption: str = None, width: str = None,
                  alt_text: str = None, align: str = None) -> None:
        """Add external image to the report.

        Args:
            path: Path to the image file.
            caption: Caption for the image.
            width: Width of the image.
            alt_text: Alternative text for the image.
            align: Alignment of the image.

        Returns:
            None

        Assumptions:
            - The image file exists at the specified path.
        """
        self.figure_counter += 1

        # Organize image
        dest_path = ImageProcessor.organize_image(path, self.output_dir, "auto")
        rel_path = ImageProcessor.get_relative_path(dest_path, self.output_dir)

        figure_id = f"fig-{self.figure_counter:03d}"
        figure_caption = caption if caption else (alt_text if alt_text else f"Figure {self.figure_counter}")

        self.add_content(f"\n\n![]({rel_path}){{#{figure_id}}}\n\n: {figure_caption}\n\n")

        if dest_path not in self.generated_images:
            self.generated_images.append(dest_path)

    def add_note(self, content: str, title: str = None, ref_id: str = None) -> str:
        """Add a note callout using components.

        Args:
            content: Content of the note.
            title: Title of the note.
            ref_id: Reference ID for the note.

        Returns:
            The reference ID of the note.

        Assumptions:
            - The note renderer is properly initialized.
        """
        callout = self.note_renderer.create_quarto_callout(content, "note", title, ref_id)
        self.add_content(f"\n\n{callout['markdown']}\n\n")
        return callout['ref_id']

    def add_warning(self, content: str, title: str = None, ref_id: str = None) -> str:
        """Add a warning callout using components.

        Args:
            content: Content of the warning.
            title: Title of the warning.
            ref_id: Reference ID for the warning.

        Returns:
            The reference ID of the warning.

        Assumptions:
            - The note renderer is properly initialized.
        """
        callout = self.note_renderer.create_quarto_callout(content, "warning", title, ref_id)
        self.add_content(f"\n\n{callout['markdown']}\n\n")
        return callout['ref_id']

    def add_error(self, content: str, title: str = None, ref_id: str = None) -> str:
        """Add an error callout using components.

        Args:
            content: Content of the error.
            title: Title of the error.
            ref_id: Reference ID for the error.

        Returns:
            The reference ID of the error.

        Assumptions:
            - The note renderer is properly initialized.
        """
        callout = self.note_renderer.create_quarto_callout(content, "caution", title, ref_id)
        self.add_content(f"\n\n{callout['markdown']}\n\n")
        return callout['ref_id']

    def add_success(self, content: str, title: str = None, ref_id: str = None) -> str:
        """Add a success callout using components.

        Args:
            content: Content of the success.
            title: Title of the success.
            ref_id: Reference ID for the success.

        Returns:
            The reference ID of the success.

        Assumptions:
            - The note renderer is properly initialized.
        """
        callout = self.note_renderer.create_quarto_callout(content, "important", title, ref_id)
        self.add_content(f"\n\n{callout['markdown']}\n\n")
        return callout['ref_id']

    def add_tip(self, content: str, title: str = None, ref_id: str = None) -> str:
        """Add a tip callout using components.

        Args:
            content: Content of the tip.
            title: Title of the tip.
            ref_id: Reference ID for the tip.

        Returns:
            The reference ID of the tip.

        Assumptions:
            - The note renderer is properly initialized.
        """
        callout = self.note_renderer.create_quarto_callout(content, "tip", title, ref_id)
        self.add_content(f"\n\n{callout['markdown']}\n\n")
        return callout['ref_id']

    def add_note_reference(self, ref_id: str, custom_text: str = None) -> str:
        """Add a cross-reference to a note callout.

        Args:
            ref_id: Reference ID of the note.
            custom_text: Custom text for the reference.

        Returns:
            The cross-reference text.

        Assumptions:
            - The note renderer is properly initialized.
        """
        reference = self.note_renderer.create_cross_reference(ref_id, custom_text)
        self.add_content(reference)
        return reference

    def add_equation(self, latex_code: str, caption: str = None, label: str = None) -> str:
        """Add equation using equations component.

        Args:
            latex_code: LaTeX code for the equation.
            caption: Caption for the equation.
            label: Label for the equation.

        Returns:
            The label of the equation.

        Assumptions:
            - The equation processor is properly initialized.
        """
        formatted = self.equation_processor.format_equation(latex_code, label, caption)
        equation_markdown = self.equation_processor.get_equation_markdown(formatted)
        self.add_content(equation_markdown)
        return formatted['label']

    def add_equation_block(self, equations: List[str], caption: str = None,
                          label: str = None, align: bool = True) -> str:
        """Add equation block using equations component.

        Args:
            equations: List of LaTeX code strings for the equations.
            caption: Caption for the equation block.
            label: Label for the equation block.
            align: Whether to align the equations.

        Returns:
            The label of the equation block.

        Assumptions:
            - The equation processor is properly initialized.
        """
        formatted = self.equation_processor.format_equation_block(equations, label, caption, align)
        equation_markdown = self.equation_processor.get_equation_markdown(formatted)
        self.add_content(equation_markdown)
        return formatted['label']

    def add_equation_in_line(self, latex_code: str) -> None:
        """Add inline equation using equations component.

        Args:
            latex_code: LaTeX code for the inline equation.

        Returns:
            None

        Assumptions:
            - The equation processor is properly initialized.
        """
        inline_equation = self.equation_processor.format_inline_equation(latex_code)
        self.add_content(inline_equation)

    def add_equation_reference(self, ref_id: str, custom_text: str = None) -> str:
        """Add equation cross-reference using equations component.

        Args:
            ref_id: Reference ID of the equation.
            custom_text: Custom text for the reference.

        Returns:
            The cross-reference text.

        Assumptions:
            - The equation processor is properly initialized.
        """
        reference = self.equation_processor.create_equation_reference(ref_id, custom_text)
        self.add_content(reference)
        return reference

    def _display_in_notebook(self, img_path: str) -> None:
        """Display image in Jupyter notebook if available.

        Args:
            img_path: Path to the image file.

        Returns:
            None

        Assumptions:
            - IPython is installed.
        """
        try:
            from IPython.display import Image, display
            display(Image(filename=img_path))
        except ImportError:
            pass

    def get_available_color_palettes(self) -> Dict[str, str]:
        """Get available color palettes.

        Args:
            None

        Returns:
            A dictionary of available color palettes.

        Assumptions:
            - The color configuration file is properly formatted.
        """
        try:
            colors_config = _load_cached_colors()
            if 'palettes' in colors_config:
                return colors_config['palettes']
            return {}
        except Exception as e:
            raise ValueError(f"Could not load color palettes: {e}")

    def generate(self, markdown: bool = False, html: bool = False, pdf: bool = False, citation_style: Optional[str] = 'ieee') -> None:
        """Generate content in requested formats with enhanced processing.

        Args:
            markdown: Generate markdown file.
            html: Generate HTML file.
            pdf: Generate PDF file.
            citation_style: Citation style for PDF/HTML generation (required if generating PDF/HTML).

        Returns:
            None

        Assumptions:
            - Quarto is installed if HTML or PDF generation is requested.
            - Citation style is valid.
        """
        if not any([markdown, html, pdf]):
            raise ValueError("No output formats requested.")

        # Citation style is required for PDF/HTML generation
        if (html or pdf) and not citation_style:
            raise ValueError("citation_style parameter is required for PDF/HTML generation")

        # Validate citation style if provided
        if citation_style:
            from ePy_docs.styler.quarto import validate_csl_style
            validate_csl_style(citation_style)  # Will raise ValueError if invalid

        # Create directory
        directory = os.path.dirname(self.file_path)
        if directory:
            os.makedirs(directory, exist_ok=True)

        base_filename = os.path.splitext(self.file_path)[0]
        markdown_path = f"{base_filename}.md"

        # Process content before writing
        content = ''.join(self.content_buffer)
        processed_content = ContentProcessor.format_content(content)

        # Algo nuevo: Add progress bar for content writing
        with open(markdown_path, 'w', encoding='utf-8') as f:
            with tqdm(total=len(processed_content), desc="Writing Content") as pbar:
                for i, char in enumerate(processed_content):
                    f.write(char)
                    pbar.update(1)

        # Generate other formats if needed
        if html or pdf:
            from ePy_docs.formats.quarto import QuartoConverter

            title = self._extract_title_from_content() or os.path.basename(base_filename)

            # Get author from project configuration - no fallbacks
            project_config = get_project_config()
            consultants = project_config.get('consultants', [])
            if consultants:
                author = consultants[0]['name']
            else:
                consultant_info = project_config['consultant']
                author = consultant_info['name']

            converter = QuartoConverter()

            if html:
                converter.convert_markdown_to_html(
                    markdown_content=markdown_path, title=title, author=author,
                    output_file=f"{base_filename}.html", clean_temp=False,
                    citation_style=citation_style
                )

            if pdf:
                converter.convert_markdown_to_pdf(
                    markdown_content=markdown_path, title=title, author=author,
                    output_file=f"{base_filename}.pdf", clean_temp=False,
                    citation_style=citation_style
                )

        # Clean up markdown file if not requested
        if not markdown and os.path.exists(markdown_path):
            import time
            time.sleep(0.5)
            try:
                os.remove(markdown_path)
            except Exception:
                pass

    def add_cover_title(self, title: str) -> None:
        """Add main title to cover page.

        Args:
            title: Title of the cover page.

        Returns:
            None
        """
        self.add_content(f"\n# {title}\n\n")

    def add_cover_subtitle(self, subtitle: str) -> None:
        """Add subtitle to cover page.

        Args:
            subtitle: Subtitle of the cover page.

        Returns:
            None
        """
        self.add_content(f"*{subtitle}*\n\n")

    def add_cover_section(self, section_title: str) -> None:
        """Add section header to cover page.

        Args:
            section_title: Title of the cover page section.

        Returns:
            None
        """
        self.add_content(f"\n## {section_title}\n\n")

    def add_cover_content(self, content: str) -> None:
        """Add content to cover page.

        Args:
            content: Content of the cover page.

        Returns:
            None
        """
        self.add_content(f"{content}\n\n")

    def add_responsability_page(self, report_config: Optional[Dict[str, Any]] = None, sync_json: bool = True) -> str:
        """Add responsibility page using copyright module.

        Args:
            report_config: Optional report configuration dictionary.
            sync_json: Whether to synchronize with the project's JSON configuration file.

        Returns:
            A message indicating the result of adding the responsibility page.

        Assumptions:
            - The responsibility module is properly configured.
        """
        try:
            from ePy_docs.project.responsible import add_responsibility_text

            # Add responsibility sections - add_responsibility_text already includes all sections
            add_responsibility_text(self)

            return "Responsibility page added successfully"

        except Exception as e:
            raise ValueError(f"Failed to add responsibility page: {e}")

    def add_copyright_footer(self, sync_json: bool = True) -> str:
        """Add copyright footer using copyright module.

        Args:
            sync_json: Whether to synchronize with the project's JSON configuration file.

        Returns:
            A message indicating the result of adding the copyright footer.

        Assumptions:
            - The copyright module is properly configured.
        """
        try:
            from ePy_docs.project.copyright import create_copyright_page

            project_config = get_project_config() if sync_json else {}
            create_copyright_page(project_config, self)

            return "Copyright footer added successfully"

        except Exception as e:
            raise ValueError(f"Failed to add copyright footer: {e}")