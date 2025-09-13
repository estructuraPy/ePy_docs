"""Markdown report generation module for ePy_docs.formats.

Provides specialized functionality for generating markdown reports with tables,
figures, notes, and other formatted content.
"""

import os
import tempfile
from typing import Dict, List, Any, Optional, Union, Tuple
import re

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from pydantic import BaseModel, Field

from ePy_docs.components.pages import _ConfigManager
from ePy_docs.components.colors import get_colors_config
# PURIFIED - Use kingdom architecture instead of legacy TextFormatter
from ePy_docs.components.text import get_text_config
from ePy_docs.components.setup import ContentProcessor
from ePy_docs.components.setup import get_absolute_output_directories
# PURIFIED - Remove contaminated tables import
# from ePy_docs.components.tables import create_table_image, create_split_table_images

# TEMPORARY COMPATIBILITY - Simple TextFormatter replacement
class TextFormatter:
    """Temporary TextFormatter replacement for compatibility."""
    
    @staticmethod
    def format_field(label, value, sync_files=False):
        """Simple text field formatter replacement."""
        if value is None:
            value = ""
        return f"**{label}:** {value}\n"

# TEMPORARY COMPATIBILITY - Simple table functions replacement
def create_table_image(*args, **kwargs):
    """Temporary replacement for create_table_image."""
    import os
    # Return a dummy path for now
    return os.path.join(os.getcwd(), "results", "figures", "table_placeholder.png")

def create_split_table_images(*args, **kwargs):
    """Temporary replacement for create_split_table_images."""
    import os
    # Return dummy paths for now
    return [os.path.join(os.getcwd(), "results", "figures", f"table_split_{i}.png") for i in range(2)]


class MarkdownFormatter(BaseModel):
    """Markdown report formatter with content management and formatting."""
    
    output_dir: str = Field(description="Output directory for generated files")
    table_counter: int = Field(default=0, description="Counter for table numbering")
    figure_counter: int = Field(default=0, description="Counter for figure numbering")
    note_counter: int = Field(default=0, description="Counter for note numbering")
    equation_counter: int = Field(default=0, description="Counter for equation numbering")
    temp_dir: str = Field(default_factory=lambda: os.path.join(tempfile.gettempdir(), 'epy_reports'))
    generated_images: List[str] = Field(default_factory=list)
    content_buffer: List[str] = Field(default_factory=list)
    show_in_notebook: bool = Field(default=True, description="Whether to display images in Jupyter notebooks")
    document_type: str = Field(description="Type of document being generated (report or paper)")

    def __init__(self, **data):
        """Initialize MarkdownFormatter with proper directory setup."""
        super().__init__(**data)
        self.output_dir = os.path.abspath(self.output_dir)
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.temp_dir, exist_ok=True)

    def _load_table_config(self, sync_files: bool = None) -> Dict[str, Any]:
        """Load complete table configuration from multiple JSON files.
        
        Args:
            sync_files: If None, uses project sync_files setting
            
        Returns:
            Unified dictionary with all table configuration parameters
        """
        # Use project sync_files setting if not specified
        if sync_files is None:
            from ePy_docs.components.setup import get_current_project_config
            current_config = get_current_project_config()
            sync_files = current_config.settings.sync_files if current_config else False
        
        from ePy_docs.components.tables import _load_table_config
        return _load_table_config()

    def _load_image_config(self, sync_files: bool = None) -> Dict[str, Any]:
        """Load complete image configuration from JSON files.
        
        Args:
            sync_files: If None, uses project sync_files setting
            
        Returns:
            Unified dictionary with all image configuration parameters
        """
        # Use project sync_files setting if not specified
        if sync_files is None:
            from ePy_docs.components.setup import get_current_project_config
            current_config = get_current_project_config()
            sync_files = current_config.settings.sync_files if current_config else False
        from ePy_docs.components.pages import _ConfigManager
        config_manager = _ConfigManager()
        return config_manager.get_config_by_path('components/images.json', sync_files)

    def _add_content(self, content: str) -> None:
        """Add content to the buffer."""
        self.content_buffer.append(content)
    
    def add_content(self, content: str) -> None:
        """Add content to the buffer preserving original formatting.
        
        This method preserves the exact formatting provided by the user,
        including line breaks, spacing, and markdown syntax. This is essential
        for maintaining Quarto-compatible markdown content.
        """
        if content:
            self.content_buffer.append(content)
    
    def _add_inline_content(self, content: str) -> None:
        """Add inline content to the buffer without adding line breaks.
        
        This method is specifically for inline elements like inline equations,
        inline code, or any content that should not force a line break.
        """
        if content:
            # For inline content, append directly to the last buffer item if it exists
            # and doesn't end with a newline, otherwise add as new item
            if self.content_buffer and not self.content_buffer[-1].endswith('\n'):
                self.content_buffer[-1] += content
            else:
                self.content_buffer.append(content)

    def add_inline_text(self, text: str) -> None:
        """Add inline text to the buffer without adding line breaks.
        
        This is for text content that should appear inline with previous content.
        """
        self._add_inline_content(text)

    def add_header(self, text: str, level: int = 1, color: Optional[str] = None) -> None:
        """Add a header with optional color styling.
        
        Args:
            text: Header text
            level: Header level (1-6, where 1 is h1, 2 is h2, etc.)
            color: Optional color for styling (color will be ignored in pure markdown mode)
        """
        if level < 1 or level > 6:
            level = 1
        
        # Siempre usar markdown puro con espacios adecuados, ignorando el color
        # El color solo se aplicaría en la fase de HTML/PDF
        header_prefix = "#" * level
        # Asegurar un espacio en blanco antes y dos después del encabezado
        self._add_content(f"\n{header_prefix} {text}\n\n")

    def add_h1(self, text: str, color: Optional[str] = None) -> None:
        """Add an H1 header."""
        self.add_header(text, 1, color)

    def add_h2(self, text: str, color: Optional[str] = None) -> None:
        """Add an H2 header."""
        self.add_header(text, 2, color)

    def add_h3(self, text: str, add_newline: bool = True, color: Optional[str] = None) -> None:
        """Add an H3 header with optional newline control."""
        # Siempre usar markdown puro con espacios adecuados, ignorando el color
        # El color solo se aplicaría en la fase de HTML/PDF
        self._add_content(f"\n### {text}")
            
        if add_newline:
            self._add_content("\n\n")
        else:
            self._add_content("\n")

    def add_text(self, content: str) -> None:
        """Add plain text content with mathematical notation processing."""
        # Ensure content is properly encoded string
        if not isinstance(content, str):
            content = str(content)
        
        # Preserve original line breaks and formatting
        processed_content = content
        
        # Apply final bullet conversion before adding to content
        processed_content = processed_content.replace('• ', '- ')
        
        # Process mathematical notation preserving LaTeX equations
        from ePy_docs.components.format import format_superscripts
        try:
            import re
            
            # First, process ${variable} patterns - these should be converted to simple LaTeX variables
            def process_math_variable(match):
                variable_content = match.group(1)
                # For variables in math expressions, just clean the variable name
                # Don't apply superscripts here - let LaTeX handle the math formatting
                return f"${variable_content}$"
            
            # Process ${variable} patterns
            processed_content = re.sub(r'\$\{([^}]+)\}', process_math_variable, processed_content)
            
            # Apply superscript formatting only to text OUTSIDE of LaTeX equations
            # Split content by LaTeX equations to preserve them
            parts = re.split(r'(\$[^$]*\$)', processed_content)
            
            formatted_parts = []
            for i, part in enumerate(parts):
                if i % 2 == 0:  # Even indices are regular text
                    # Apply superscript formatting to regular text
                    formatted_part = format_superscripts(part, 'html', self.sync_files)
                    formatted_parts.append(formatted_part)
                else:  # Odd indices are LaTeX equations - preserve them exactly
                    formatted_parts.append(part)
            
            processed_content = ''.join(formatted_parts)
            
        except Exception as e:
            # If mathematical processing fails, continue without it
            print(f"WARNING: Mathematical processing failed: {e}")
            pass
            
        # Preserve line breaks: if content has line breaks, respect them
        if '\n' in processed_content:
            # Content already has formatting, add minimal spacing
            self._add_content(f"{processed_content}\n\n")
        else:
            # Single line content, add standard spacing
            self._add_content(f"{processed_content}\n\n")

    def add_table(self, df: pd.DataFrame, title: str = None,
                          dpi: int = 300, palette_name: str = 'YlOrRd',
                          hide_columns: Union[str, List[str]] = None,
                          filter_by: Union[Tuple[str, Union[str, int, float, List]], List[Tuple[str, Union[str, int, float, List]]]] = None,
                          sort_by: Union[str, Tuple[str, str], List[Union[str, Tuple[str, str]]]] = None,
                          split_large_tables: bool = True,
                          max_rows_per_table: Optional[int] = None) -> None:
        """Generate a clean table with only header coloring.
        
        Args:
            df: DataFrame to display
            title: Optional title for the table
            dpi: Image resolution
            palette_name: Color palette for styling
            hide_columns: Column name(s) to hide from the table
            filter_by: Filter rows by column content
            sort_by: Sort rows by column(s)
            split_large_tables: Whether to automatically split large tables
            max_rows_per_table: Maximum rows per table before splitting
            
        Returns:
            List of paths to the generated image files
        """
        # Get dynamic output directories from setup.json as absolute paths
        output_dirs = get_absolute_output_directories(document_type=self.document_type)
        tables_dir = output_dirs['tables']
        os.makedirs(tables_dir, exist_ok=True)
        
        try:
            if split_large_tables:
                img_paths = create_split_table_images(
                    df=df,
                    output_dir=tables_dir,
                    base_table_number=self.table_counter + 1,
                    title=title,
                    highlight_columns=[],  # Empty list = no coloring for simple tables
                    palette_name=palette_name,
                    dpi=dpi,
                    hide_columns=hide_columns,
                    filter_by=filter_by,
                    sort_by=sort_by,
                    max_rows_per_table=max_rows_per_table
                )
                # Increment counter by the number of tables created
                self.table_counter += len(img_paths)
            else:
                img_path = create_table_image(
                    df=df,
                    output_dir=tables_dir,
                    table_number=self.table_counter + 1,
                    title=title,
                    highlight_columns=[],
                    palette_name=palette_name,
                    dpi=dpi,
                    hide_columns=hide_columns,
                    filter_by=filter_by,
                    sort_by=sort_by
                )
                img_paths = [img_path]
                self.table_counter += 1
        except Exception as e:
            # If table generation fails, add text fallback instead of broken image references
            self.markdown_content += f"\n**Table: {title}**\n\n"
            self.markdown_content += "*(Table image could not be generated)*\n\n"
            self.markdown_content += f"Error: {str(e)}\n\n"
            return []

        # Add table content to markdown with proper spacing and Windows-style paths
        for i, img_path in enumerate(img_paths):
            # Convertir a path relativo con estilo Windows
            rel_path = os.path.relpath(img_path, self.output_dir).replace('/', os.sep)
            if not rel_path.startswith('.'):
                rel_path = '.' + os.sep + rel_path
                
            # Añadir con espacios antes y después para correcta renderización
            self._add_content("\n\n")
            
            # Each split table gets its own sequential number
            table_number = self.table_counter - len(img_paths) + i + 1
            
            # Create caption - no part information needed since each has its own number
            if title:
                caption = f"Tabla {table_number}: {title}"
            else:
                caption = f"Tabla {table_number}"
            
            # Create table ID for cross-referencing - use sequential numbering
            table_id = f"tbl-{table_number}"
            
            # Load configuration and get fig_width - use HTML-specific width if available
            table_config = self._load_table_config()
            display_config = table_config['display']
            
            # Use HTML-specific width for better sizing in HTML output
            if display_config['html_responsive']:
                fig_width = display_config['max_width_inches_html']
                # Add responsive classes for better HTML display
                html_classes = "quarto-figure-center table-figure"
                responsive_attrs = f'width="{display_config.get("html_max_width_percent", 90)}%"'
            else:
                fig_width = display_config['max_width_inches']
                html_classes = "quarto-figure-center"
                responsive_attrs = ""
            
            # Use Quarto table syntax with enhanced formatting for better HTML display
            if responsive_attrs:
                self._add_content(f'![{caption}]({rel_path}){{#{table_id} fig-width={fig_width} .{html_classes} {responsive_attrs}}}\n\n')
            else:
                self._add_content(f'![{caption}]({rel_path}){{#{table_id} fig-width={fig_width} .{html_classes}}}\n\n')
            
            self.generated_images.append(img_path)
            
            if self.show_in_notebook:
                self._display_in_notebook(img_path)
        
        # Don't return paths to avoid printing them in notebooks/console
        return None

    def add_colored_table(self, df: pd.DataFrame, title: str = None,
                                  palette_name: str = None, 
                                  highlight_columns: Optional[List[str]] = None,
                                  dpi: int = 300,
                                  hide_columns: Union[str, List[str]] = None,
                                  filter_by: Union[Tuple[str, Union[str, int, float, List]], List[Tuple[str, Union[str, int, float, List]]]] = None,
                                  sort_by: Union[str, Tuple[str, str], List[Union[str, Tuple[str, str]]]] = None,
                                  n_rows: Optional[int] = None,
                                  split_large_tables: bool = True,
                                  max_rows_per_table: Optional[int] = None) -> None:
        """Add a table with intelligent colored cells based on highlight_columns.
        
        Args:
            df: DataFrame to display
            title: Optional title for the table
            palette_name: Color palette for numeric columns
            highlight_columns: Columns to apply intelligent coloring to
            dpi: Image resolution
            hide_columns: Column name(s) to hide from the table
            filter_by: Filter rows by column content
            sort_by: Sort rows by column(s)
            n_rows: Limit number of rows to show after filters and sort
            split_large_tables: Whether to automatically split large tables
            max_rows_per_table: Maximum rows per table before splitting
            
        Returns:
            List of paths to the generated image files
        """
        if palette_name is None:
            palette_name = 'YlOrRd'
        
        # Get dynamic output directories from setup.json as absolute paths
        output_dirs = get_absolute_output_directories(document_type=self.document_type)
        tables_dir = output_dirs['tables']
        os.makedirs(tables_dir, exist_ok=True)
        
        try:
            if split_large_tables:
                img_paths = create_split_table_images(
                    df=df,
                    output_dir=tables_dir,
                    base_table_number=self.table_counter + 1,
                    title=title,
                    highlight_columns=highlight_columns,
                    palette_name=palette_name,
                    dpi=dpi,
                    hide_columns=hide_columns,
                    filter_by=filter_by,
                    sort_by=sort_by,
                    n_rows=n_rows,
                    max_rows_per_table=max_rows_per_table
                )
                # Increment counter by the number of tables created
                self.table_counter += len(img_paths)
            else:
                img_path = create_table_image(
                    df=df,
                    output_dir=tables_dir,
                    table_number=self.table_counter + 1,
                    title=title,
                    highlight_columns=highlight_columns,
                    palette_name=palette_name,
                    dpi=dpi,
                    hide_columns=hide_columns,
                    filter_by=filter_by,
                    sort_by=sort_by,
                    n_rows=n_rows
                )
                img_paths = [img_path]
                self.table_counter += 1
        except Exception as e:
            # If table generation fails, add text fallback instead of broken image references
            self.markdown_content += f"\n**Table: {title}**\n\n"
            self.markdown_content += "*(Table image could not be generated)*\n\n"
            self.markdown_content += f"Error: {str(e)}\n\n"
            return []

        # Add table content to markdown with proper spacing and Windows-style paths
        for i, img_path in enumerate(img_paths):
            # Convertir a path relativo con estilo Windows
            rel_path = os.path.relpath(img_path, self.output_dir).replace('/', os.sep)
            if not rel_path.startswith('.'):
                rel_path = '.' + os.sep + rel_path
                
            # Añadir con espacios antes y después para correcta renderización
            self._add_content("\n\n")
            
            # Each split table gets its own sequential number
            table_number = self.table_counter - len(img_paths) + i + 1
            
            # Create caption - no part information needed since each has its own number
            if title:
                caption = f"Tabla {table_number}: {title}"
            else:
                caption = f"Tabla {table_number}"
            
            # Create table ID for cross-referencing - use sequential numbering
            table_id = f"tbl-{table_number}"
            
            # Load configuration and get fig_width - use HTML-specific width if available
            table_config = self._load_table_config()
            display_config = table_config['display']
            
            # Use HTML-specific width for better sizing in HTML output
            if display_config['html_responsive']:
                fig_width = display_config['max_width_inches_html']
                # Add aggressive responsive styling for better HTML display - colors from COLORS kingdom
                from ePy_docs.components.colors import get_color_from_path
                border_color = get_color_from_path('blues.medium', 'hex')
                shadow_color = get_color_from_path('blues.medium', 'hex')  # Convert to rgba with opacity
                html_classes = "quarto-figure-center table-figure"
                responsive_attrs = f'width="{display_config.get("html_max_width_percent", 85)}%" style="transform: scale(1.1); border: 3px solid {border_color}; box-shadow: 0 10px 20px {shadow_color}33;"'
            else:
                fig_width = display_config['max_width_inches']
                html_classes = "quarto-figure-center"
                responsive_attrs = ""
            
            # Use Quarto table syntax with enhanced formatting for better HTML display
            if responsive_attrs:
                self._add_content(f'![{caption}]({rel_path}){{#{table_id} fig-width={fig_width} .{html_classes} {responsive_attrs}}}\n\n')
            else:
                self._add_content(f'![{caption}]({rel_path}){{#{table_id} fig-width={fig_width} .{html_classes}}}\n\n')
            
            self.generated_images.append(img_path)
            
            if self.show_in_notebook:
                self._display_in_notebook(img_path)
        
        # Don't return paths to avoid printing them in notebooks/console
        return None

    def add_plot(self, title=None, filename=None, fig=None, caption=None, 
                width_inches=None, height_inches=None, dpi=300):
        """Add plot to the report with proper colors, numbering and captioning."""
        if fig is None:
            raise ValueError("No figure provided to add_plot")
        
        if width_inches is not None or height_inches is not None:
            if width_inches is None:
                width_inches = height_inches
            if height_inches is None:
                height_inches = width_inches
            fig.set_size_inches(width_inches, height_inches)
        
        self.figure_counter += 1
        img_filename = f"figure_{self.figure_counter}.png"
        
        # Use dynamic path system for figures directory as absolute paths
        output_dirs = get_absolute_output_directories(document_type=self.document_type)
        figures_dir = output_dirs['figures']
        os.makedirs(figures_dir, exist_ok=True)
        img_path = os.path.join(figures_dir, img_filename)
        
        # Add title and caption directly to the figure
        if title or caption:
            fig.subplots_adjust(bottom=0.15)
            
            if title:
                try:
                    ax = fig.gca()
                except:
                    ax = fig.add_axes([0, 0, 1, 1])
                    ax.axis('off')
                ax.text(0.01, 0.99, title, transform=ax.transAxes, 
                       fontsize=14, fontweight='bold', va='top', ha='left')
            
            caption_text = caption if caption and caption != title else title
            if caption_text:
                try:
                    ax = fig.gca()
                except:
                    if not title:
                        ax = fig.add_axes([0, 0, 1, 1])
                        ax.axis('off')
                ax.text(0.01, 0.01, f"Figura {self.figure_counter}: {caption_text}", 
                       transform=ax.transAxes, fontsize=12, fontweight='bold', va='bottom', ha='left')
        
        fig.savefig(img_path, bbox_inches='tight', dpi=dpi, facecolor='white', edgecolor='none')
        
        if self.show_in_notebook:
            self._display_in_notebook(img_path)
        
        # Convertir a path relativo usando forward slashes para compatibilidad web
        rel_path = os.path.relpath(img_path, self.output_dir).replace(os.sep, '/')
        if not rel_path.startswith('.'):
            rel_path = './' + rel_path
            
        # Añadir con espacios antes y después para correcta renderización
        self._add_content("\n\n")
        
        # Use proper Quarto format for figures with captions
        caption_text = caption if caption else title
        
        # Use descriptive alt text for Quarto compatibility
        # Quarto automatically adds "Figura X" using fig-prefix
        if caption_text:
            alt_text = caption_text
        else:
            alt_text = ""
        
        # Create figure ID for cross-referencing
        figure_id = f"fig-{self.figure_counter}"
        
        # Build image markdown with proper Quarto format
        img_markdown = f"![{alt_text}]({rel_path}) {{#{figure_id}}}"
        self._add_content(img_markdown)
        
        # Add caption using Quarto syntax if there's a caption
        if caption_text:
            self._add_content(f"\n: {caption_text}")
        
        self._add_content("\n\n")
        
        self.generated_images.append(img_path)
        return img_path

    def add_image(self, path: str, caption: str = None, width: str = None, 
                  alt_text: str = None, align: str = None, label: str = None):
        """Add an external image to the report using Quarto figure syntax with cross-reference support.
        
        Args:
            path: Path to the image file
            caption: Optional caption for the image
            width: Width specification (applied in Quarto format)
            alt_text: Alternative text for the image
            align: Alignment (applied in Quarto format)
            label: Optional label for cross-referencing (e.g., "structural-diagram"). 
                   If None, will use sequential numbering (fig-1, fig-2, etc.)
                   
        Returns:
            The figure label used for cross-referencing
        """
        import shutil
        
        self.figure_counter += 1
        
        try:
            # Copy image to output directory if needed
            dest_path = path
            if os.path.exists(path) and os.path.dirname(os.path.abspath(path)) != os.path.abspath(self.output_dir):
                # Determine appropriate subdirectory using ImageProcessor
                from ePy_docs.components.images import ImageProcessor
                # Get dynamic figures directory from setup.json as absolute paths
                output_dirs = get_absolute_output_directories(document_type=self.document_type)
                figures_dir = output_dirs['figures']
                dest_path = ImageProcessor.organize_image(path, os.path.dirname(figures_dir), os.path.basename(figures_dir))
                self.generated_images.append(dest_path)
            
            # Convert to Windows-style relative path
            if os.path.isabs(dest_path):
                rel_path = os.path.relpath(dest_path, self.output_dir).replace('/', os.sep)
                if not rel_path.startswith('.'):
                    rel_path = '.' + os.sep + rel_path
            else:
                rel_path = dest_path.replace('/', os.sep)
                if not rel_path.startswith('.'):
                    rel_path = '.' + os.sep + rel_path
                    
            # Create figure label - use custom label if provided, otherwise use sequential numbering
            if label is None:
                figure_id = f"fig-{self.figure_counter}"
            else:
                # Use custom label but ensure it follows fig- convention for cross-references
                if not label.startswith('fig-'):
                    figure_id = f"fig-{label}"
                else:
                    figure_id = label
                    
            # Prepare alt text for Quarto compatibility 
            # Quarto automatically adds "Figura X" using fig-prefix, so alt text should be descriptive
            if alt_text:
                img_alt = alt_text
            elif caption:
                # Use the caption as alt text if available
                img_alt = caption
            else:
                # Use empty alt text to let Quarto handle the numbering
                img_alt = ""
                
            # Add content with proper spacing
            self._add_content("\n\n")
            
            # Build image markdown with Quarto format for proper PDF generation
            # Use the alt text that was prepared earlier (line 507-514)
            img_markdown = f"![{img_alt}]({rel_path})"
            
            # Build attributes for Quarto - simplified for better PDF compatibility
            attributes = []
            if width:
                attributes.append(f'width="{width}"')
            if align:
                attributes.append(f'fig-align="{align}"')
            
            # Add the figure ID for cross-referencing - this is critical for Quarto
            attributes.append(f'#{figure_id}')
            
            # Apply attributes with proper Quarto syntax
            if attributes:
                img_markdown += " {" + " ".join(attributes) + "}"
            
            self._add_content(img_markdown)
            
            # Add caption using proper Quarto syntax for PDF compatibility
            if caption:
                self._add_content(f"\n: {caption}")
            
            self._add_content("\n\n")
            
        except Exception as e:
            raise ValueError(f"Failed to add image: {e}")
        
        return figure_id

    def _ensure_note_renderer(self):
        """Ensure note renderer is initialized."""
        if not hasattr(self, '_note_renderer'):
            from ePy_docs.components.notes import NoteRenderer
            self._note_renderer = NoteRenderer()
            # Sync counters
            self._note_renderer.note_counter = self.note_counter

    def add_note(self, content: str, title: str = None, ref_id: str = None) -> str:
        """Add an informational note callout."""
        self._ensure_note_renderer()
        # Don't generate title with counter if no title provided
        result = self._note_renderer.create_quarto_callout(content, "note", title, ref_id)
        self._add_content(result['markdown'])
        self.note_counter = self._note_renderer.note_counter
        return result['ref_id']

    def add_warning(self, content: str, title: str = None, ref_id: str = None) -> str:
        """Add a warning callout."""
        self._ensure_note_renderer()
        # Don't generate title with counter if no title provided
        result = self._note_renderer.create_quarto_callout(content, "warning", title, ref_id)
        self._add_content(result['markdown'])
        self.note_counter = self._note_renderer.note_counter
        return result['ref_id']

    def add_error(self, content: str, title: str = None, ref_id: str = None) -> str:
        """Add an error callout."""
        self._ensure_note_renderer()
        if title is None:
            title = f"Error {self._note_renderer.note_counter + 1}"
        result = self._note_renderer.create_quarto_callout(content, "caution", title, ref_id)
        self._add_content(result['markdown'])
        self.note_counter = self._note_renderer.note_counter
        return result['ref_id']

    def add_success(self, content: str, title: str = None, ref_id: str = None) -> str:
        """Add a success callout."""
        self._ensure_note_renderer()
        if title is None:
            title = f"Éxito {self._note_renderer.note_counter + 1}"
        result = self._note_renderer.create_quarto_callout(content, "important", title, ref_id)
        self._add_content(result['markdown'])
        self.note_counter = self._note_renderer.note_counter
        return result['ref_id']

    def add_tip(self, content: str, title: str = None, ref_id: str = None) -> str:
        """Add a tip callout."""
        self._ensure_note_renderer()
        if title is None:
            title = f"Consejo {self._note_renderer.note_counter + 1}"
        result = self._note_renderer.create_quarto_callout(content, "tip", title, ref_id)
        self._add_content(result['markdown'])
        self.note_counter = self._note_renderer.note_counter
        return result['ref_id']

    def _display_in_notebook(self, img_path: str) -> None:
        """Display image in Jupyter notebook if available."""
        if not self.show_in_notebook:
            return
        
        try:
            from IPython.display import Image, display
            from IPython import get_ipython
            from ePy_docs.components.setup import _load_cached_config
            
            if get_ipython() is not None:
                if os.path.exists(img_path):
                    units_config = _load_cached_config('units')
                    image_width = units_config['display']['formatting']['image_display_width']
                    display(Image(img_path, width=image_width))
        except (ImportError, Exception):
            # Silently skip display if not in Jupyter or any other error
            pass

    def save_to_file(self, file_path: str) -> str:
        """Save the markdown content to a file, ensuring all image paths are properly formatted.
        
        Args:
            file_path: Path to save the markdown file
            
        Returns:
            Absolute path to the saved file
        """
        file_path = os.path.abspath(file_path)
        directory = os.path.dirname(file_path)
        if directory:
            os.makedirs(directory, exist_ok=True)
        
        # Obtener todo el contenido markdown y procesarlo
        markdown_content = ''.join(self.content_buffer)
        
        # Procesar todas las rutas de imágenes para asegurar que sean relativas y en formato Windows
        processed_markdown = self._fix_image_paths_in_markdown(markdown_content)
        
        try:
            from ePy_docs.api.file_manager import write_text
            write_text(processed_markdown, file_path)
        except Exception as e:
            raise RuntimeError(f"Failed to write markdown file {file_path}: {e}")
            
        return file_path
        
    def _fix_image_paths_in_markdown(self, markdown_content: str) -> str:
        """Fix image paths in markdown to use Windows-style relative paths while preserving Quarto attributes.
        
        Converts all image references to use the format: ![alt](./subdirectory/image.png) {#fig-1}
        while preserving any Quarto attributes like {#fig-1}, {width="50%"}, etc.
        
        Args:
            markdown_content: Original markdown content
            
        Returns:
            Markdown content with fixed image paths and preserved attributes
        """
        # Updated pattern to capture Quarto attributes: ![alt](path) {attributes}
        img_pattern = re.compile(r'!\[(.*?)\]\(([^)]+)\)(\s*\{[^}]*\})?')
        
        def fix_path(match):
            alt_text = match.group(1)
            img_path = match.group(2)
            attributes = match.group(3) or ""  # Capture Quarto attributes if present
            
            # If it's an absolute path, convert to relative from output_dir
            if os.path.isabs(img_path):
                try:
                    # Create relative path from output_dir using Windows style
                    rel_path = os.path.relpath(img_path, self.output_dir)
                    # Always use backslashes for Windows paths in markdown
                    rel_path = '.' + os.sep + rel_path.replace('/', os.sep)
                except ValueError:
                    # If paths are on different drives, keep the original
                    rel_path = img_path
            else:
                # If it's already relative but uses forward slashes, convert to backslashes
                rel_path = img_path.replace('/', os.sep)
                # Ensure it starts with .\ if not already
                if not rel_path.startswith('.'):
                    rel_path = '.' + os.sep + rel_path
            
            # Return image with preserved attributes
            return f'![{alt_text}]({rel_path}){attributes}'
        
        # Fix all image paths while preserving Quarto attributes
        return img_pattern.sub(fix_path, markdown_content)

    @staticmethod
    def fix_image_paths_in_imported_content(content: str, source_file_path: str, 
                                          output_dir: str, figure_counter: int = 0,
                                          document_type: str = "report") -> tuple[str, int]:
        """Fix image paths in imported content to work in the current document context.
        
        This is a utility function for processing imported markdown/quarto files
        that contain image references with relative paths.
        
        Args:
            content: The content to process
            source_file_path: Path of the source file being imported
            output_dir: Output directory where figures should be copied
            figure_counter: Current figure counter (will be incremented)
            
        Returns:
            Tuple of (processed_content, updated_figure_counter)
        """
        import re
        import shutil
        
        # Get the directory of the source file
        source_dir = os.path.dirname(os.path.abspath(source_file_path))
        
        # Create figures directory in current output using dynamic path from setup.json
        output_dirs = get_absolute_output_directories(document_type=document_type)
        figures_dir = output_dirs['figures']
        os.makedirs(figures_dir, exist_ok=True)
        
        # Pattern to match markdown images: ![alt](path) or ![alt](path){attributes}
        img_pattern = r'!\[([^\]]*)\]\(([^)]+)\)(\{[^}]*\})?'
        
        def replace_image(match):
            nonlocal figure_counter
            
            alt_text = match.group(1)
            img_path = match.group(2)
            attributes = match.group(3) or ""
            
            # Skip if it's already a relative path to figures/ or an absolute URL
            # Get dynamic figures directory name from setup.json
            output_dirs = get_absolute_output_directories(document_type=document_type)
            figures_dir_name = os.path.basename(output_dirs['figures'])
            if img_path.startswith(('http://', 'https://', f'{figures_dir_name}/', f'./{figures_dir_name}/')):
                return match.group(0)
            
            # Resolve the absolute path of the image relative to the source file
            if os.path.isabs(img_path):
                abs_img_path = img_path
            else:
                abs_img_path = os.path.join(source_dir, img_path)
            
            # Check if the image exists
            if os.path.exists(abs_img_path):
                # Increment figure counter and copy image
                figure_counter += 1
                
                # Get file extension
                _, ext = os.path.splitext(abs_img_path)
                new_filename = f"figure_{figure_counter}{ext}"
                dest_path = os.path.join(figures_dir, new_filename)
                
                # Copy image to figures directory
                shutil.copy2(abs_img_path, dest_path)
                
                # Create relative path from output directory
                from ePy_docs.components.images import ImageProcessor
                rel_path = ImageProcessor.get_quarto_relative_path(dest_path, output_dir)
                
                # Update attributes to include figure ID if not present
                figure_id = f"fig-{figure_counter}"
                if attributes:
                    # Check if there's already a figure ID in the attributes
                    if not re.search(r'#fig-\w+', attributes):
                        # Add figure ID to existing attributes
                        attributes = attributes.rstrip('}') + f' #{figure_id}' + '}'
                    # If there's already a figure ID, preserve the original attributes
                else:
                    # Create new attributes with figure ID
                    attributes = f' {{#{figure_id}}}'
                
                return f"![{alt_text}]({rel_path}){attributes}"
            else:
                # Image not found, keep original but add warning comment
                return f"<!-- WARNING: Image not found: {abs_img_path} -->\n{match.group(0)}"
        
        # Replace all image references
        updated_content = re.sub(img_pattern, replace_image, content)
        
        return updated_content, figure_counter

    def get_content(self) -> str:
        """Get the current markdown content as a string."""
        return ''.join(self.content_buffer)

    def clear_content(self) -> None:
        """Clear the content buffer."""
        self.content_buffer = []

    def get_available_color_palettes(self) -> Dict[str, str]:
        """Get available color palettes for table styling."""
        config = _ConfigManager()
        colors_data = config.get_colors_config()
        
        palettes = {}
        
        # Add standard matplotlib palettes
        for name in ['Blues', 'Greens', 'Reds', 'Oranges', 'Purples', 'YlOrRd', 'viridis', 'plasma']:
            palettes[name] = f"Matplotlib {name} palette"
            
        # Add custom palettes from config
        if colors_data and "reports" in colors_data and "tables" in colors_data["reports"] and "palettes" in colors_data["reports"]["tables"]:
            tables_palettes = colors_data["reports"]["tables"]["palettes"]
            for name, colors in tables_palettes.items():
                palettes[name] = f"Custom palette: {name}"
            
        return palettes

    @staticmethod
    def process_text_content(text: str) -> str:
        """Centralized text processing for consistent markdown handling across modules.
        
        Args:
            text: Input text that may contain markdown
            
        Returns:
            Processed text with consistent formatting including mathematical notation
        """
        if not text:
            return ""
        
        # Ensure proper string handling and preserve formatting
        if not isinstance(text, str):
            text = str(text)
            
        result = text.strip()
        
        # Process mathematical notation using the correct format for HTML output
        from ePy_docs.components.format import format_superscripts
        try:
            # First, process ${variable} patterns to apply superscript formatting to variables
            import re
            def process_math_variable(match):
                variable_content = match.group(1)
                # Apply superscript formatting to the variable content
                formatted_content = format_superscripts(variable_content, 'html', False)
                # Return as LaTeX math notation
                return f"${formatted_content}$"
            
            # Process ${variable} patterns
            result = re.sub(r'\$\{([^}]+)\}', process_math_variable, result)
            
            # Then apply general superscript processing to the rest of the content
            result = format_superscripts(result, 'html', False)
        except Exception as e:
            # If mathematical processing fails, continue without it
            print(f"WARNING: Mathematical processing failed in process_text_content: {e}")
            pass
        except Exception:
            # If mathematical processing fails, continue without it
            pass
        
        # Enhanced header processing - preserve markdown headers for note processing
        for i in range(6, 0, -1):
            header_pattern = r'(^|\n)#{' + str(i) + r'}\s+(.+?)(\n|$)'
            replacement = r'\1' + '#' * i + r' \2\n\n'
            result = re.sub(header_pattern, replacement, result)
        
        # Preserve image syntax with better spacing - updated to handle Quarto attributes
        # Pattern matches: ![alt](path) or ![alt](path) {attributes}
        result = re.sub(r'([^\n])(!\[.*?\]\(.*?\)(\s*\{[^}]*\})?)', r'\1\n\n\2', result)
        result = re.sub(r'(!\[.*?\]\(.*?\)(\s*\{[^}]*\})?)([^\n])', r'\1\n\n\3', result)
        
        # Normalize line endings
        result = re.sub(r'\r\n', '\n', result)
        
        # Clean up multiple blank lines but preserve intentional spacing
        result = re.sub(r'\n{3,}', '\n\n', result)
        
        # Clean trailing whitespace from lines
        result = re.sub(r'[ \t]+$', '', result, flags=re.MULTILINE)
        
        # Preserve all line breaks - only remove leading/trailing whitespace from entire text if it's just whitespace
        # Do NOT strip if there's actual content to preserve user-defined formatting
        if result.strip():
            return result  # Keep original line breaks intact
        else:
            return result.strip()  # Only strip if content is essentially empty

    def add_equation(self, latex_code: str, caption: str = None, label: str = None) -> str:
        """Add a block equation that will be numbered by Quarto.
        
        Args:
            latex_code: The LaTeX equation code (can be with or without $ delimiters, multiline accepted)
            caption: Optional caption for the equation
            label: Optional label for cross-referencing
            
        Returns:
            Label for the equation
        """
        if not latex_code:
            raise ValueError("LaTeX code cannot be empty")
            
        self.equation_counter += 1
        
        # Create equation label if not provided
        if label is None:
            label = f"eq-{self.equation_counter}"
        
        # Check if the equation already has proper Quarto format (multiline with label)
        latex_stripped = latex_code.strip()
        if (latex_stripped.startswith('$$') and 
            '{#' in latex_stripped and '}' in latex_stripped):
            # Already properly formatted with label - preserve exactly as is
            equation_with_label = latex_stripped
        elif (latex_stripped.startswith('$$') and 
              latex_stripped.endswith('$$') and 
              '\n' in latex_stripped):
            # Multiline equation without label - add label to closing $$
            lines = latex_stripped.split('\n')
            for i in range(len(lines) - 1, -1, -1):
                if lines[i].strip() == '$$':
                    lines[i] = f"$$ {{#{label}}}"
                    break
            equation_with_label = '\n'.join(lines)
        else:
            # Single line or needs formatting
            if latex_stripped.startswith('$$') and latex_stripped.endswith('$$'):
                # Remove the $$ delimiters to reconstruct properly
                clean_latex = latex_stripped[2:-2].strip()
            else:
                clean_latex = latex_stripped
            
            # Create single-line equation format for Quarto: $$ equation $$ {#label}
            equation_with_label = f"$$ {clean_latex} $$ {{#{label}}}"
        
        # Add equation using Quarto syntax for numbering
        if caption:
            self._add_content(f"\n\n{equation_with_label}\n\n: {caption}\n\n")
        else:
            self._add_content(f"\n\n{equation_with_label}\n\n")
        
        return label

    def add_equation_in_line(self, latex_code: str) -> None:
        """Add an inline equation that will NOT be numbered by Quarto.
        
        Args:
            latex_code: The LaTeX equation code (without $ delimiters)
        """
        if not latex_code:
            raise ValueError("LaTeX code cannot be empty")
            
        # Use single $ for inline math (not numbered)
        if latex_code.startswith('$') and latex_code.endswith('$'):
            equation_text = latex_code
        else:
            equation_text = f"${latex_code}$"
        
        # Add inline equation directly to content (no numbering)
        self._add_inline_content(equation_text)

    def add_equation_block(self, equations: List[str], caption: str = None, label: str = None, align: bool = True) -> str:
        """Add a block of multiple equations that will be numbered by Quarto.
        
        Args:
            equations: List of LaTeX equation strings (or single multiline string)
            caption: Optional caption for the equation block
            label: Optional label for cross-referencing
            align: Whether to align the equations (ignored if input is already formatted)
            
        Returns:
            Label for the equation block
        """
        if not equations:
            raise ValueError("Equations list cannot be empty")
            
        self.equation_counter += 1
        
        # Create equation label if not provided
        if label is None:
            label = f"eq-{self.equation_counter}"
        
        # If there's only one equation and it's already properly formatted, preserve it
        if len(equations) == 1:
            eq = equations[0].strip()
            if (eq.startswith('$$') and eq.endswith('$$') and '\n' in eq):
                # Already formatted multiline equation - preserve it
                if '{#' in eq and '}' in eq:
                    # Already has label
                    equation_block = eq
                else:
                    # Add label to closing $$
                    lines = eq.split('\n')
                    for i in range(len(lines) - 1, -1, -1):
                        if lines[i].strip() == '$$':
                            lines[i] = f"$$ {{#{label}}}"
                            break
                    equation_block = '\n'.join(lines)
            else:
                # Process as before for non-formatted equations
                if eq.startswith('$$') and eq.endswith('$$'):
                    equation_block = eq
                else:
                    equation_block = f"$${eq}$$"
                    
                # Add label
                lines = equation_block.split('\n')
                if len(lines) >= 2 and lines[-1] == '$$':
                    lines[-1] = f"$$ {{#{label}}}"
                    equation_block = '\n'.join(lines)
                else:
                    equation_block = equation_block.rstrip() + f" {{#{label}}}"
        else:
            # Multiple equations - build aligned equation block
            if align and len(equations) > 1:
                equation_block = "$$\n\\begin{align}\n"
                for i, eq in enumerate(equations):
                    # Clean equation
                    clean_eq = eq.strip()
                    if clean_eq.startswith('$') and clean_eq.endswith('$'):
                        clean_eq = clean_eq[1:-1]
                    if clean_eq.startswith('$$') and clean_eq.endswith('$$'):
                        clean_eq = clean_eq[2:-2]
                    
                    # Add line break for all except last equation
                    if i < len(equations) - 1:
                        equation_block += f"{clean_eq} \\\\\n"
                    else:
                        equation_block += f"{clean_eq}\n"
                equation_block += f"\\end{{align}}\n$$ {{#{label}}}"
            else:
                # Unaligned block
                equation_block = "$$\n" + "\n".join(equations) + f"\n$$ {{#{label}}}"
        
        # Add equation block using Quarto syntax for numbering
        if caption:
            self._add_content(f"\n\n{equation_block}\n\n: {caption}\n\n")
        else:
            self._add_content(f"\n\n{equation_block}\n\n")
        
        return label
        
    def add_crossref(self, ref_type: str, ref_id: Union[str, int], custom_text: str = None) -> str:
        """Add a cross-reference to a figure, table, equation, or note callout.
        
        Args:
            ref_type: Type of reference ('fig', 'tbl', 'eq', 'note')
            ref_id: ID of the referenced element (number or string)
            custom_text: Optional custom text instead of default reference
            
        Returns:
            The cross-reference markdown that was added
        """
        ref_type = ref_type.lower()
        
        # Handle note callouts differently
        if ref_type == 'note':
            self._ensure_note_renderer()
            ref_markdown = self._note_renderer.create_cross_reference(ref_id, custom_text)
            self._add_content(ref_markdown)
            return ref_markdown
        
        # Handle figures, tables, and equations
        if ref_type not in ['fig', 'tbl', 'eq']:
            raise ValueError(f"ref_type must be 'fig', 'tbl', 'eq', or 'note', got '{ref_type}'")
        
        # Convert numeric IDs to proper format
        if isinstance(ref_id, int):
            if ref_type == 'fig':
                full_ref_id = f"fig-{ref_id}"
            elif ref_type == 'tbl':
                full_ref_id = f"tbl-{ref_id}"
            else:  # eq
                full_ref_id = f"eq-{ref_id}"
        else:
            # Assume it's already properly formatted or a custom ID
            full_ref_id = ref_id
            if not full_ref_id.startswith(f"{ref_type}-"):
                full_ref_id = f"{ref_type}-{full_ref_id}"
        
        if custom_text:
            crossref_markdown = f"[{custom_text}](#{full_ref_id})"
        else:
            crossref_markdown = f"@{full_ref_id}"
        
        self._add_content(crossref_markdown)
        return crossref_markdown
    
    def add_cross_reference(self, ref_id, text=None):
        """Add a cross-reference to a previously created callout. 
        
        This is a convenience method that calls add_crossref with 'note' type.
        
        Args:
            ref_id: Reference ID of the callout
            text: Optional custom text for the reference
            
        Returns:
            Reference markdown string
        """
        return self.add_crossref('note', ref_id, text)
        
    def get_cross_references_list(self):
        """Get a list of all cross-references created.
        
        Returns:
            Dictionary with all cross-references
        """
        self._ensure_note_renderer()
        return self._note_renderer.get_cross_references_list()
    
    def add_figure_ref(self, figure_number: Union[str, int], custom_text: str = None) -> str:
        """Add a reference to a figure. Convenience method for add_crossref.
        
        Args:
            figure_number: Figure number or ID
            custom_text: Optional custom text instead of "Figura X"
            
        Returns:
            The cross-reference markdown that was added
        """
        return self.add_crossref('fig', figure_number, custom_text)
    
    def add_note_ref(self, note_ref_id: Union[str, int], custom_text: str = None) -> str:
        """Add a reference to a note callout. Convenience method for add_crossref.
        
        Args:
            note_ref_id: Note reference ID
            custom_text: Optional custom text instead of auto-generated text
            
        Returns:
            The cross-reference markdown that was added
        """
        return self.add_crossref('note', note_ref_id, custom_text)
    
    def add_table_ref(self, table_number: Union[str, int], custom_text: str = None) -> str:
        """Add a reference to a table. Convenience method for add_crossref.
        
        Args:
            table_number: Table number or ID
            custom_text: Optional custom text instead of "Tabla X"
            
        Returns:
            The cross-reference markdown that was added
        """
        return self.add_crossref('tbl', table_number, custom_text)
    
    def add_equation_ref(self, equation_id: Union[str, int], custom_text: str = None) -> str:
        """Add a reference to an equation. Convenience method for add_crossref.
        
        Args:
            equation_id: Equation ID or number
            custom_text: Optional custom text instead of "Ec. X"
            
        Returns:
            The cross-reference markdown that was added
        """
        return self.add_crossref('eq', equation_id, custom_text)
