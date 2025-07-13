"""Report formatter for ePy_docs - Advanced formatting for technical reports.

Provides comprehensive report generation capabilities with tables, figures,
equations, and professional layouts. Reduced from original 1000+ lines by
delegating specialized functionality to component modules.
"""

import os
import tempfile
from typing import Dict, List, Any, Optional, Union, Tuple
import datetime

import pandas as pd
import matplotlib.pyplot as plt
from pydantic import BaseModel, Field

from ePy_docs.core.base import WriteFiles
from ePy_docs.core.content import ContentProcessor
from ePy_docs.core.text import TextFormatter
from ePy_docs.components.tables import create_table_image, create_split_table_images
from ePy_docs.components.images import ImageProcessor
from ePy_docs.components.notes import NoteRenderer
from ePy_docs.styler.colors import get_color, _load_cached_colors
from ePy_docs.styler.setup import get_config_value, get_project_config


class ReportFormatter(WriteFiles):
    """Advanced formatter for technical and academic reports."""
    
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

    # Table methods using components
    def add_table(self, df: pd.DataFrame, title: str = None,
                          dpi: int = 300, hide_columns: Union[str, List[str]] = None,
                          filter_by: Union[Tuple, List[Tuple]] = None,
                          sort_by: Union[str, Tuple, List] = None,
                          split_large_tables: bool = True,
                          max_rows_per_table: Optional[int] = None,
                          n_rows: Optional[int] = None,
                          label: str = None, caption: str = None) -> List[str]:
        """Generate table using components module."""
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
        
        # Add tables to markdown with Quarto labels
        for i, img_path in enumerate(img_paths):
            rel_path = ImageProcessor.get_relative_path(img_path, self.output_dir)
            
            # Create table ID and caption
            if len(img_paths) > 1:
                table_id = f"tbl-{label}-{i+1}" if label else f"tbl-{self.table_counter:03d}-{i+1}"
                table_caption = f"{title} (Parte {i+1}/{len(img_paths)})" if title else f"Table {self.table_counter} (Parte {i+1}/{len(img_paths)})"
            else:
                table_id = f"tbl-{label}" if label else f"tbl-{self.table_counter:03d}"
                table_caption = caption if caption else title
            
            if table_caption:
                self.add_content(f"\n\n![{table_caption}]({rel_path}){{#{table_id}}}\n\n")
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
        """Generate colored table."""
        # For colored tables, we need to use the full functionality from components
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

        # Add table content to markdown with proper spacing and Windows-style paths
        for i, img_path in enumerate(img_paths):
            # Use ImageProcessor for consistent path handling
            rel_path = ImageProcessor.get_relative_path(img_path, self.output_dir)
            
            # Create table ID and caption using same system as add_table()
            if len(img_paths) > 1:
                table_id = f"tbl-{self.table_counter:03d}-{i+1}"
                table_caption = f"{title} (Parte {i+1}/{len(img_paths)})" if title else f"Tabla {self.table_counter} (Parte {i+1}/{len(img_paths)})"
            else:
                table_id = f"tbl-{self.table_counter:03d}"
                table_caption = title if title else f"Tabla {self.table_counter}"
            
            # Add table with Quarto label format
            if table_caption:
                self.add_content(f"\n\n![{table_caption}]({rel_path}){{#{table_id}}}\n\n")
            else:
                self.add_content(f"\n\n![]({rel_path}){{#{table_id}}}\n\n")
            
            self.generated_images.append(img_path)
            if self.show_in_notebook:
                self._display_in_notebook(img_path)
        
        return img_paths

    # Plot methods - can be moved to plotter module in future
    def add_plot(self, title=None, filename=None, fig=None, caption=None, 
                width_inches=None, height_inches=None, dpi=300):
        """Add plot to the report with proper numbering."""
        if fig is None:
            fig = plt.gcf()
        
        if width_inches or height_inches:
            if width_inches and not height_inches:
                height_inches = width_inches
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
            fig.subplots_adjust(bottom=0.15)
            if title:
                try:
                    ax = fig.gca()
                    ax.text(0.01, 0.99, title, transform=ax.transAxes, 
                           fontsize=14, fontweight='bold', va='top', ha='left')
                except:
                    pass
        
        fig.savefig(img_path, bbox_inches='tight', dpi=dpi, facecolor='white', edgecolor='none')
        
        if self.show_in_notebook:
            self._display_in_notebook(img_path)
        
        # Add to markdown
        rel_path = ImageProcessor.get_relative_path(img_path, self.output_dir)
        figure_id = f"fig-{self.figure_counter:03d}"
        
        if caption:
            self.add_content(f"\n\n![{caption}]({rel_path}){{#{figure_id}}}\n\n")
        else:
            self.add_content(f"\n\n![]({rel_path}){{#{figure_id}}}\n\n")
        
        self.generated_images.append(img_path)
        return img_path

    def add_image(self, path: str, caption: str = None, width: str = None, 
                  alt_text: str = None, align: str = None):
        """Add external image to the report."""
        self.figure_counter += 1
        
        # Organize image
        dest_path = ImageProcessor.organize_image(path, self.output_dir, "auto")
        rel_path = ImageProcessor.get_relative_path(dest_path, self.output_dir)
        
        figure_id = f"fig-{self.figure_counter}"
        figure_caption = caption if caption else (alt_text if alt_text else f"Figure {self.figure_counter}")
        
        self.add_content(f"\n\n![{figure_caption}]({rel_path}){{#{figure_id}}}\n\n")
        
        if dest_path not in self.generated_images:
            self.generated_images.append(dest_path)

    # Note methods using components
    def add_note(self, content, title=None, max_lines_per_note=None):
        """Add a note callout."""
        self._add_styled_note(content, title, "note", max_lines_per_note)

    def add_warning(self, content, title=None, max_lines_per_note=None):
        """Add a warning callout."""
        self._add_styled_note(content, title, "warning", max_lines_per_note)

    def add_error(self, content, title=None, max_lines_per_note=None):
        """Add an error callout."""
        self._add_styled_note(content, title, "error", max_lines_per_note)

    def add_success(self, content, title=None, max_lines_per_note=None):
        """Add a success callout."""
        self._add_styled_note(content, title, "success", max_lines_per_note)

    def add_tip(self, content, title=None, max_lines_per_note=None):
        """Add a tip callout."""
        self._add_styled_note(content, title, "tip", max_lines_per_note)

    def _add_styled_note(self, content, title, note_type="note", max_lines_per_note=None):
        """Add styled note using components."""
        self.note_counter = self.note_renderer.increment_counter()
        
        # Format content using note renderer
        formatted_content = self.note_renderer.format_note_content(content, note_type)
        
        # Add as Quarto callout
        note_title = title if title else note_type.capitalize()
        self.add_content(f"\n\n::: {{.callout-{note_type}}}\n")
        self.add_content(f"## {note_title}\n\n")
        self.add_content(f"{formatted_content}\n")
        self.add_content(":::\n\n")

    # Equation methods using LaTeX for Quarto
    def add_equation(self, latex_code: str, caption: str = None, label: str = None) -> str:
        """Add equation using LaTeX for Quarto rendering."""
        self.equation_counter += 1
        
        if label is None:
            label = f"eq-{self.equation_counter:03d}"
        
        # Ensure proper equation formatting
        equation_text = latex_code.strip()
        if not (equation_text.startswith('$$') and equation_text.endswith('$$')):
            equation_text = f"$${equation_text}$$"
        
        if caption:
            self.add_content(f"\n\n{equation_text} {{#{label}}}\n\n: {caption}\n\n")
        else:
            self.add_content(f"\n\n{equation_text} {{#{label}}}\n\n")
        
        return label

    def add_equation_in_line(self, latex_code: str) -> None:
        """Add inline equation."""
        equation_text = latex_code.strip()
        if not (equation_text.startswith('$') and equation_text.endswith('$')):
            equation_text = f"${equation_text}$"
        
        self.add_content(equation_text)

    # Utility methods
    def _display_in_notebook(self, img_path: str) -> None:
        """Display image in Jupyter notebook if available."""
        try:
            from IPython.display import Image, display
            display(Image(filename=img_path))
        except ImportError:
            pass

    def get_available_color_palettes(self) -> Dict[str, str]:
        """Get available color palettes."""
        try:
            colors_config = _load_cached_colors()
            if 'palettes' in colors_config:
                return colors_config['palettes']
            return {}
        except Exception as e:
            raise ValueError(f"Could not load color palettes: {e}")

    # Enhanced generation with better content processing
    def generate(self, markdown: bool = False, html: bool = False, pdf: bool = False, citation_style: Optional[str] = 'ieee') -> None:
        """Generate content in requested formats with enhanced processing.
        
        Args:
            markdown: Generate markdown file
            html: Generate HTML file  
            pdf: Generate PDF file
            citation_style: Citation style for PDF/HTML generation (required if generating PDF/HTML)
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
        
        # Write markdown
        with open(markdown_path, 'w', encoding='utf-8') as f:
            if processed_content and not processed_content.endswith('\n'):
                processed_content += '\n'
            f.write(processed_content)
        
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

    # Cover and responsibility methods (can be moved to covers module)
    def add_cover_title(self, title: str) -> None:
        """Add main title to cover page."""
        self.add_content(f"\n# {title}\n\n")

    def add_cover_subtitle(self, subtitle: str) -> None:
        """Add subtitle to cover page."""
        self.add_content(f"*{subtitle}*\n\n")

    def add_cover_section(self, section_title: str) -> None:
        """Add section header to cover page."""
        self.add_content(f"\n## {section_title}\n\n")

    def add_cover_content(self, content: str) -> None:
        """Add content to cover page."""
        self.add_content(f"{content}\n\n")

    def add_responsability_page(self, report_config: Optional[Dict[str, Any]] = None, sync_json: bool = True) -> str:
        """Add responsibility page using copyright module."""
        try:
            from ePy_docs.project.responsible import add_responsibility_text
            
            # Add responsibility sections - add_responsibility_text already includes all sections
            add_responsibility_text(self)
            
            return "Responsibility page added successfully"
        
        except Exception as e:
            raise ValueError(f"Failed to add responsibility page: {e}")

    def add_copyright_footer(self, sync_json: bool = True) -> str:
        """Add copyright footer using copyright module."""
        try:
            from ePy_docs.project.copyright import create_copyright_page
            
            project_config = get_project_config() if sync_json else {}
            create_copyright_page(project_config, self)
            
            return "Copyright footer added successfully"
        
        except Exception as e:
            raise ValueError(f"Failed to add copyright footer: {e}")
