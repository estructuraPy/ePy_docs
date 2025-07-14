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

from ePy_docs.styler.setup import _ConfigManager
from ePy_docs.styler.colors import get_color, get_custom_colormap
from ePy_docs.core.text import TextFormatter
from ePy_docs.core.content import ContentProcessor
from ePy_docs.components.tables import create_table_image, create_split_table_images


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

    def __init__(self, **data):
        """Initialize MarkdownFormatter with proper directory setup."""
        super().__init__(**data)
        self.output_dir = os.path.abspath(self.output_dir)
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.temp_dir, exist_ok=True)

    def _add_content(self, content: str) -> None:
        """Add content to the buffer."""
        self.content_buffer.append(content)

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
        """Add plain text content."""
        # Apply final bullet conversion before adding to content
        processed_content = content.replace('• ', '- ')
        self._add_content(f"{processed_content}\n\n")

    def add_table(self, df: pd.DataFrame, title: str = None,
                          dpi: int = 300, palette_name: str = 'YlOrRd',
                          hide_columns: Union[str, List[str]] = None,
                          filter_by: Union[Tuple[str, Union[str, int, float, List]], List[Tuple[str, Union[str, int, float, List]]]] = None,
                          sort_by: Union[str, Tuple[str, str], List[Union[str, Tuple[str, str]]]] = None,
                          split_large_tables: bool = True,
                          max_rows_per_table: Optional[int] = None) -> List[str]:
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
        # Ensure tables are saved in tables/ subdirectory
        tables_output_dir = os.path.join(self.output_dir, "tables")
        os.makedirs(tables_output_dir, exist_ok=True)
        
        if split_large_tables:
            img_paths = create_split_table_images(
                df=df,
                output_dir=tables_output_dir,
                base_table_number=self.table_counter + 1,
                title=title,
                highlight_columns=[],  # Empty list = no coloring for simple tables
                palette_name=palette_name,
                dpi=dpi,
                hide_columns=hide_columns,
                filter_by=filter_by,
                sort_by=sort_by,
                max_rows_per_table=max_rows_per_table,
                print_title_in_image=False  # Keep images clean - title will be in Quarto caption
            )
            self.table_counter += 1  # Increment by 1 regardless of splits
        else:
            img_path = create_table_image(
                df=df,
                output_dir=tables_output_dir,
                table_number=self.table_counter + 1,
                title=title,
                highlight_columns=[],
                palette_name=palette_name,
                dpi=dpi,
                hide_columns=hide_columns,
                filter_by=filter_by,
                sort_by=sort_by,
                print_title_in_image=False  # Keep titles clean in images, part info will be in Quarto captions
            )
            img_paths = [img_path]
            self.table_counter += 1

        # Add table content to markdown with proper spacing and Windows-style paths
        for i, img_path in enumerate(img_paths):
            # Convertir a path relativo con estilo Windows
            rel_path = os.path.relpath(img_path, self.output_dir).replace('/', os.sep)
            if not rel_path.startswith('.'):
                rel_path = '.' + os.sep + rel_path
                
            # Añadir con espacios antes y después para correcta renderización
            self._add_content("\n\n")
            
            # Create caption with part info if multiple tables
            if len(img_paths) > 1:
                # Multiple tables - add "(Parte n/m)" to caption
                if title:
                    # Load table title format configuration
                    from ePy_docs.styler.setup import get_styles_config
                    styles_config = get_styles_config()
                    table_style = styles_config['pdf_settings']['table_style']
                    
                    base_caption = f"Tabla {self.table_counter}: {title}"
                    caption_with_part = table_style['multi_table_title_format'].format(
                        title=base_caption,
                        part=i+1,
                        total=len(img_paths)
                    )
                    caption = caption_with_part
                else:
                    # No title provided, use the no-title format
                    from ePy_docs.styler.setup import get_styles_config
                    styles_config = get_styles_config()
                    table_style = styles_config['pdf_settings']['table_style']
                    
                    base_caption = f"Tabla {self.table_counter}"
                    caption = table_style['multi_table_title_format'].format(
                        title=base_caption,
                        part=i+1,
                        total=len(img_paths)
                    )
            else:
                # Single table - use original format
                caption = f"Tabla {self.table_counter}" if title is None else f"Tabla {self.table_counter}: {title}"
            
            # Create table ID for cross-referencing
            table_id = f"tbl-{self.table_counter}"
            if len(img_paths) > 1:
                table_id += f"-{i+1}"
            
            # Use Quarto table syntax instead of figure syntax
            self._add_content(f"![{caption}]({rel_path}){{#{table_id}}}\n\n")
            
            self.generated_images.append(img_path)
            
            if self.show_in_notebook:
                self._display_in_notebook(img_path)
        
        return img_paths

    def add_colored_table(self, df: pd.DataFrame, title: str = None,
                                  palette_name: str = None, 
                                  highlight_columns: Optional[List[str]] = None,
                                  dpi: int = 300,
                                  hide_columns: Union[str, List[str]] = None,
                                  filter_by: Union[Tuple[str, Union[str, int, float, List]], List[Tuple[str, Union[str, int, float, List]]]] = None,
                                  sort_by: Union[str, Tuple[str, str], List[Union[str, Tuple[str, str]]]] = None,
                                  n_rows: Optional[int] = None,
                                  split_large_tables: bool = True,
                                  max_rows_per_table: Optional[int] = None) -> List[str]:
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
        
        # Ensure tables are saved in tables/ subdirectory
        tables_output_dir = os.path.join(self.output_dir, "tables")
        os.makedirs(tables_output_dir, exist_ok=True)
        
        if split_large_tables:
            img_paths = create_split_table_images(
                df=df,
                output_dir=tables_output_dir,
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
            self.table_counter += 1  # Increment by 1 regardless of splits
        else:
            img_path = create_table_image(
                df=df,
                output_dir=tables_output_dir,
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

        # Add table content to markdown with proper spacing and Windows-style paths
        for i, img_path in enumerate(img_paths):
            # Convertir a path relativo con estilo Windows
            rel_path = os.path.relpath(img_path, self.output_dir).replace('/', os.sep)
            if not rel_path.startswith('.'):
                rel_path = '.' + os.sep + rel_path
                
            # Añadir con espacios antes y después para correcta renderización
            self._add_content("\n\n")
            
            # Create caption with part info if multiple tables
            if len(img_paths) > 1:
                # Multiple tables - add "(Parte n/m)" to caption
                if title:
                    # Load table title format configuration
                    from ePy_docs.styler.setup import get_styles_config
                    styles_config = get_styles_config()
                    table_style = styles_config['pdf_settings']['table_style']
                    
                    base_caption = f"Tabla {self.table_counter}: {title}"
                    caption_with_part = table_style['multi_table_title_format'].format(
                        title=base_caption,
                        part=i+1,
                        total=len(img_paths)
                    )
                    caption = caption_with_part
                else:
                    # No title provided, use the no-title format
                    from ePy_docs.styler.setup import get_styles_config
                    styles_config = get_styles_config()
                    table_style = styles_config['pdf_settings']['table_style']
                    
                    base_caption = f"Tabla {self.table_counter}"
                    caption = table_style['multi_table_title_format'].format(
                        title=base_caption,
                        part=i+1,
                        total=len(img_paths)
                    )
            else:
                # Single table - use original format
                caption = f"Tabla {self.table_counter}" if title is None else f"Tabla {self.table_counter}: {title}"
            
            # Create table ID for cross-referencing
            table_id = f"tbl-{self.table_counter}"
            if len(img_paths) > 1:
                table_id += f"-{i+1}"
            
            # Use Quarto table syntax instead of figure syntax
            self._add_content(f"![{caption}]({rel_path}){{#{table_id}}}\n\n")
            
            self.generated_images.append(img_path)
            
            if self.show_in_notebook:
                self._display_in_notebook(img_path)
        
        return img_paths

    def add_plot(self, title=None, filename=None, fig=None, caption=None, 
                width_inches=None, height_inches=None, dpi=300):
        """Add plot to the report with proper colors, numbering and captioning."""
        if fig is None:
            print("Warning: No figure provided to add_plot")
            return
        
        try:
            if width_inches is not None or height_inches is not None:
                if width_inches is None:
                    width_inches = height_inches
                if height_inches is None:
                    height_inches = width_inches
                fig.set_size_inches(width_inches, height_inches)
            
            self.figure_counter += 1
            img_filename = f"figure_{self.figure_counter:03d}.png"
            img_path = os.path.join(self.output_dir, img_filename)
            
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
            
            # Convertir a path relativo con estilo Windows
            rel_path = os.path.relpath(img_path, self.output_dir).replace('/', os.sep)
            if not rel_path.startswith('.'):
                rel_path = '.' + os.sep + rel_path
                
            # Añadir con espacios antes y después para correcta renderización
            self._add_content("\n\n")
            caption_text = caption if caption else title
            alt_text = f"Figura {self.figure_counter}" if caption_text else f"Figura {self.figure_counter}"
            if caption_text:
                alt_text += f": {caption_text}"
            
            # Create figure ID for cross-referencing
            figure_id = f"fig-{self.figure_counter}"
            
            self._add_content(f"![{alt_text}]({rel_path}) {{#{figure_id}}}")
            self._add_content("\n\n")
            
            self.generated_images.append(img_path)
            print(f"✓ Added plot: {img_filename}")
            return img_path
            
        except Exception as e:
            print(f"Error adding plot: {e}")
            return None

    def add_image(self, path: str, caption: str = None, width: str = None, 
                  alt_text: str = None, align: str = None, label: str = None):
        """Add an external image to the report using Quarto figure syntax with cross-reference support.
        
        Args:
            path: Path to the image file
            caption: Optional caption for the image
            width: Width specification (applied in Quarto format)
            alt_text: Alternative text for the image
            align: Alignment (applied in Quarto format)
            label: Optional label for cross-referencing (e.g., "structural-diagram")
        """
        import shutil
        
        self.figure_counter += 1
        
        try:
            # Copy image to output directory if needed
            dest_path = path
            if os.path.exists(path) and os.path.dirname(os.path.abspath(path)) != os.path.abspath(self.output_dir):
                # Determine appropriate subdirectory
                if 'figures' in path.lower() or 'figure' in os.path.basename(path).lower():
                    subdir = "figures"
                elif 'tables' in path.lower() or 'table' in os.path.basename(path).lower():
                    subdir = "tables"
                elif 'notes' in path.lower() or 'note' in os.path.basename(path).lower():
                    subdir = "notes"
                else:
                    subdir = "figures"  # default
                
                # Create destination directory
                dest_dir = os.path.join(self.output_dir, subdir)
                os.makedirs(dest_dir, exist_ok=True)
                dest_path = os.path.join(dest_dir, os.path.basename(path))
                
                # Copy the file if needed
                if path != dest_path:
                    shutil.copy2(path, dest_path)
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
                    
            # Create figure label if not provided
            if label is None:
                label = f"fig-{self.figure_counter:03d}"
            
            # Prepare alt text
            if alt_text:
                img_alt = alt_text
            else:
                img_alt = caption or f"Figura {self.figure_counter}"
                
            # Create Quarto figure syntax with cross-reference support
            self._add_content("\n\n")
            
            # Start with image markdown
            img_markdown = f"![{img_alt}]({rel_path})"
            
            # Add figure attributes for Quarto
            attributes = []
            if width:
                attributes.append(f'width="{width}"')
            if align:
                attributes.append(f'fig-align="{align}"')
            
            # Add the figure label for cross-referencing
            attributes.append(f'#{label}')
            
            if attributes:
                img_markdown += " {" + " ".join(attributes) + "}"
            else:
                img_markdown += f" {{#{label}}}"
            
            self._add_content(img_markdown)
            
            # Add caption using Quarto syntax
            if caption:
                self._add_content(f"\n\n: {caption}")
            
            self._add_content("\n\n")
            
        except Exception as e:
            # En caso de error, agregamos una nota sobre el error pero sin fallbacks
            error_msg = f"Error al agregar imagen: {e}"
            self._add_content(f"\n\n[ERROR: {error_msg}]\n\n")
            raise ValueError(f"Failed to add image: {e}")
        
        return label

    def add_note(self, content, title=None, note_type="note", max_lines_per_note=None):
        """Add styled note block using specialized image generator with sequential numbering.
        
        Args:
            content: Note content
            title: Optional title for the note
            note_type: Type of note ('note', 'warning', 'error', 'success', 'tip')
            max_lines_per_note: Optional override for max lines per note
        """
        self.note_counter += 1
        
        try:
            from ePy_docs.components.notes import NoteRenderer
            
            # Create notes directory if it doesn't exist
            notes_dir = os.path.join(self.output_dir, "notes")
            os.makedirs(notes_dir, exist_ok=True)
            
            # Procesar el contenido
            formatted_content = ContentProcessor.format_content(content)
            
            # Generar las imágenes de notas
            note_renderer = NoteRenderer()
            note_paths = note_renderer.create_multiple_note_images(
                content=formatted_content,
                note_type=note_type,
                title=title or f"{note_type.title()}",
                output_dir=notes_dir,
                note_number=self.note_counter,
                max_lines_per_note=max_lines_per_note
            )
            
            if note_paths:
                # Add all generated note images using pure markdown
                for i, note_path in enumerate(note_paths):
                    if os.path.exists(note_path):
                        # Convertir a path relativo con estilo Windows
                        rel_path = os.path.relpath(note_path, self.output_dir).replace('/', os.sep)
                        if not rel_path.startswith('.'):
                            rel_path = '.' + os.sep + rel_path
                            
                        # Crear el texto alternativo
                        note_title = title or f"{note_type.title()}"
                        if len(note_paths) > 1:
                            alt_text = f"{self.note_counter} {i+1}/{len(note_paths)}: {note_title}"
                        else:
                            alt_text = f"{self.note_counter}: {note_title}"
                        
                        # Añadir con espacios antes y después para correcta renderización
                        self._add_content("\n\n")
                        self._add_content(f"![{alt_text}]({rel_path})")
                        self._add_content("\n\n")
                        
                        self.generated_images.append(note_path)
            else:
                raise ValueError("Note image generation failed - no images created")
                
        except Exception as e:
            # No fallbacks - si falla, lanzar un error claro
            raise ValueError(f"Failed to create note image: {e}. Please check that the note configuration is correctly set in the styles.json file.")

    def add_warning(self, content, title=None):
        """Add warning note."""
        self.add_note(content, title, "warning")

    def add_error(self, content, title=None):
        """Add error note."""
        self.add_note(content, title, "error")

    def add_success(self, content, title=None):
        """Add success note."""
        self.add_note(content, title, "success")

    def add_tip(self, content, title=None):
        """Add tip note."""
        self.add_note(content, title, "tip")

    def _display_in_notebook(self, img_path: str) -> None:
        """Display image in Jupyter notebook if available."""
        if not self.show_in_notebook:
            return
        
        try:
            from IPython.display import Image, display
            from IPython import get_ipython
            
            if get_ipython() is not None:
                if os.path.exists(img_path):
                    display(Image(img_path, width=800))
                else:
                    print(f"⚠️ Warning: Image not found at {img_path}")
        except ImportError:
            print(f"📁 Image saved to: {img_path}")
        except Exception as e:
            print(f"⚠️ Warning: Could not display image in notebook: {e}")
            print(f"📁 Image saved to: {img_path}")

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
            
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(processed_markdown)
            
        return file_path
        
    def _fix_image_paths_in_markdown(self, markdown_content: str) -> str:
        """Fix image paths in markdown to use Windows-style relative paths.
        
        Converts all image references to use the format: ![alt](./subdirectory/image.png)
        
        Args:
            markdown_content: Original markdown content
            
        Returns:
            Markdown content with fixed image paths
        """
        # Fix all image paths
        img_pattern = re.compile(r'!\[(.*?)\]\(([^)]+)\)')
        
        def fix_path(match):
            alt_text = match.group(1)
            img_path = match.group(2)
            
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
                    
            return f'![{alt_text}]({rel_path})'
        
        # Fix all image paths
        return img_pattern.sub(fix_path, markdown_content)

    def get_content(self) -> str:
        """Get the current markdown content as a string."""
        return ''.join(self.content_buffer)

    def clear_content(self) -> None:
        """Clear the content buffer."""
        self.content_buffer = []

    def get_available_color_palettes(self) -> Dict[str, str]:
        """Get available color palettes for table styling."""
        try:
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
        except Exception as e:
            print(f"Warning: Could not load color palettes: {e}")
            return {"YlOrRd": "Default gradient palette"}

    @staticmethod
    def process_text_content(text: str) -> str:
        """Centralized text processing for consistent markdown handling across modules.
        
        Args:
            text: Input text that may contain markdown
            
        Returns:
            Processed text with consistent formatting
        """
        if not text:
            return ""
            
        result = text.strip()
        
        # Enhanced header processing - preserve markdown headers for note processing
        for i in range(6, 0, -1):
            header_pattern = r'(^|\n)#{' + str(i) + r'}\s+(.+?)(\n|$)'
            replacement = r'\1' + '#' * i + r' \2\n\n'
            result = re.sub(header_pattern, replacement, result)
        
        # Preserve image syntax with better spacing
        result = re.sub(r'([^\n])(!\[.*?\]\(.*?\))', r'\1\n\n\2', result)
        result = re.sub(r'(!\[.*?\]\(.*?\))([^\n])', r'\1\n\n\2', result)
        
        # Normalize line endings
        result = re.sub(r'\r\n', '\n', result)
        
        # Clean up multiple blank lines but preserve intentional spacing
        result = re.sub(r'\n{3,}', '\n\n', result)
        
        # Clean trailing whitespace from lines
        result = re.sub(r'[ \t]+$', '', result, flags=re.MULTILINE)
        
        return result.strip()

    def add_equation(self, latex_code: str, caption: str = None, label: str = None) -> str:
        """Add a block equation that will be numbered by Quarto.
        
        Args:
            latex_code: The LaTeX equation code (without $ delimiters)
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
            label = f"eq-{self.equation_counter:03d}"
        
        # Handle LaTeX code formatting - ensure proper single-line format for Quarto
        if latex_code.startswith('$$') and latex_code.endswith('$$'):
            # Remove the $$ delimiters to reconstruct properly
            clean_latex = latex_code[2:-2].strip()
        else:
            clean_latex = latex_code.strip()
        
        # Create single-line equation format for Quarto: $$ equation $$ {#label}
        equation_with_label = f"$$ {clean_latex} $$ {{#{label}}}"
        
        # Add equation using Quarto syntax for numbering
        if caption:
            self._add_content(f"\n\n{equation_with_label}\n\n: {caption}\n\n")
        else:
            self._add_content(f"\n\n{equation_with_label}\n\n")
        
        print(f"📐 Ecuación {self.equation_counter}: {caption or 'Sin título'}")
        
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
        self._add_content(equation_text)

    def add_equation_block(self, equations: List[str], caption: str = None, label: str = None, align: bool = True) -> str:
        """Add a block of multiple equations that will be numbered by Quarto.
        
        Args:
            equations: List of LaTeX equation strings
            caption: Optional caption for the equation block
            label: Optional label for cross-referencing
            align: Whether to align the equations
            
        Returns:
            Label for the equation block
        """
        if not equations:
            raise ValueError("Equations list cannot be empty")
            
        self.equation_counter += 1
        
        # Create equation label if not provided
        if label is None:
            label = f"eq-{self.equation_counter:03d}"
        
        # Build aligned equation block
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
            equation_block += "\\end{align}\n$$"
        else:
            # Single equation or unaligned block
            if len(equations) == 1:
                eq = equations[0].strip()
                if eq.startswith('$$') and eq.endswith('$$'):
                    equation_block = eq
                else:
                    equation_block = f"$${eq}$$"
            else:
                equation_block = "$$\n" + "\n".join(equations) + "\n$$"
        
        # Add equation block using Quarto syntax for numbering
        if caption:
            # Add label on same line as closing $$ for proper Quarto formatting
            lines = equation_block.split('\n')
            if len(lines) >= 2 and lines[-1] == '$$':
                lines[-1] = f"$$ {{#{label}}}"
                equation_with_label = '\n'.join(lines)
            else:
                equation_with_label = equation_block.rstrip() + f" {{#{label}}}"
            self._add_content(f"\n\n{equation_with_label}\n\n: {caption}\n\n")
        else:
            # Add label on same line as closing $$ for proper Quarto formatting
            lines = equation_block.split('\n')
            if len(lines) >= 2 and lines[-1] == '$$':
                lines[-1] = f"$$ {{#{label}}}"
                equation_with_label = '\n'.join(lines)
            else:
                equation_with_label = equation_block.rstrip() + f" {{#{label}}}"
            self._add_content(f"\n\n{equation_with_label}\n\n")
        
        print(f"📐 Bloque de ecuaciones {self.equation_counter}: {caption or 'Sin título'}")
        
        return label

    def add_quarto_callout(self, content, title, callout_type="note", ref_id=None):
        """Add Quarto callout block with optional cross-reference support.
        
        Args:
            content: Callout content
            title: Callout title  
            callout_type: Type of callout (note, warning, caution, important, tip)
            ref_id: Optional reference ID for cross-referencing (e.g., "note-analysis")
        """
        # Configuración de callouts desde JSON
        quarto_config = self._load_quarto_config()
        callout_config = quarto_config.get('callouts', {}).get(callout_type, {})
        
        # Determinar configuración del callout
        collapse = callout_config.get('collapse', False)
        icon = callout_config.get('icon', True)
        appearance = callout_config.get('appearance', 'default')
        
        # Construir opciones del callout
        options = []
        if collapse:
            options.append('collapse="true"')
        if not icon:
            options.append('icon="false"')
        if appearance != 'default':
            options.append(f'appearance="{appearance}"')
            
        options_str = ' '.join(options)
        if options_str:
            options_str = ' ' + options_str
            
        # Incrementar contador para referencias cruzadas automáticas
        self.note_counter += 1
        
        # Generar ID de referencia si no se proporciona
        if ref_id is None:
            ref_id = f"{callout_type}-{self.note_counter:03d}"
        
        # Construir contenido del callout con referencia cruzada
        callout_content = f"\n\n::: {{{callout_type}{options_str}}} {{#{ref_id}}}\n"
        callout_content += f"## {title}\n\n"
        callout_content += f"{content}\n"
        callout_content += ":::\n\n"
        
        self._add_content(callout_content)
        
        # Guardar la referencia para uso posterior
        if not hasattr(self, '_cross_references'):
            self._cross_references = {}
        self._cross_references[ref_id] = {
            'type': callout_type,
            'title': title,
            'number': self.note_counter
        }
        
        return ref_id  # Retornar el ID para referencias posteriores

    def add_note_callout(self, content, title=None, ref_id=None):
        """Add informational note using Quarto callout syntax with cross-reference support."""
        if not title:
            title = f"Nota {self.note_counter + 1}"
        return self.add_quarto_callout(content, title, "note", ref_id)

    def add_warning_callout(self, content, title=None, ref_id=None):
        """Add warning note using Quarto callout syntax with cross-reference support."""
        if not title:
            title = f"Advertencia {self.note_counter + 1}"
        return self.add_quarto_callout(content, title, "warning", ref_id)

    def add_error_callout(self, content, title=None, ref_id=None):
        """Add error note using Quarto callout syntax with cross-reference support."""
        if not title:
            title = f"Error {self.note_counter + 1}"
        return self.add_quarto_callout(content, title, "caution", ref_id)

    def add_success_callout(self, content, title=None, ref_id=None):
        """Add success note using Quarto callout syntax with cross-reference support."""
        if not title:
            title = f"Éxito {self.note_counter + 1}"
        return self.add_quarto_callout(content, title, "important", ref_id)

    def add_tip_callout(self, content, title=None, ref_id=None):
        """Add tip note using Quarto callout syntax with cross-reference support."""
        if not title:
            title = f"Consejo {self.note_counter + 1}"
        return self.add_quarto_callout(content, title, "tip", ref_id)
        
    def add_cross_reference(self, ref_id, text=None):
        """Add a cross-reference to a previously created callout.
        
        Args:
            ref_id: Reference ID of the callout
            text: Optional custom text for the reference
            
        Returns:
            Reference markdown string
        """
        if not hasattr(self, '_cross_references') or ref_id not in self._cross_references:
            # Si no existe la referencia, crear una referencia básica
            ref_text = text or f"ver @{ref_id}"
            self._add_content(f"({ref_text})")
            return
            
        ref_info = self._cross_references[ref_id]
        
        if text is None:
            # Generar texto automático basado en el tipo y número
            type_names = {
                'note': 'Nota',
                'warning': 'Advertencia', 
                'caution': 'Error',
                'important': 'Éxito',
                'tip': 'Consejo'
            }
            type_name = type_names.get(ref_info['type'], ref_info['type'].title())
            text = f"{type_name} {ref_info['number']}"
            
        # Crear referencia cruzada usando sintaxis de Quarto
        ref_markdown = f"@{ref_id}"
        self._add_content(f"({text}: {ref_markdown})")
        
    def get_cross_references_list(self):
        """Get a list of all cross-references created.
        
        Returns:
            Dictionary with all cross-references
        """
        return getattr(self, '_cross_references', {})

    def add_crossref(self, ref_type: str, ref_id: Union[str, int], custom_text: str = None) -> str:
        """Add a cross-reference to a figure, table, or equation.
        
        Args:
            ref_type: Type of reference ('fig', 'tbl', 'eq')
            ref_id: ID of the referenced element (number or string)
            custom_text: Optional custom text instead of default reference
            
        Returns:
            The cross-reference markdown that was added
        """
        ref_type = ref_type.lower()
        if ref_type not in ['fig', 'tbl', 'eq']:
            raise ValueError(f"ref_type must be 'fig', 'tbl', or 'eq', got '{ref_type}'")
        
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
    
    def add_figure_ref(self, figure_number: Union[str, int], custom_text: str = None) -> str:
        """Add a reference to a figure. Convenience method for add_crossref.
        
        Args:
            figure_number: Figure number or ID
            custom_text: Optional custom text instead of "Figura X"
            
        Returns:
            The cross-reference markdown that was added
        """
        return self.add_crossref('fig', figure_number, custom_text)
    
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
