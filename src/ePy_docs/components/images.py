"""Image processing and management for reports and presentations."""

import json
import os
import shutil
from pathlib import Path
from typing import Dict, Optional, Union

class ImageProcessor:
    """Processor for image handling across different output formats."""

    def __init__(self, config_path: Optional[str] = None):
        """Initialize ImageProcessor with configuration.
        
        Args:
            config_path: Path to the configuration file
        """
        self.config = self._load_config(config_path)
        self._counter = 1  # Initialize counter for auto-numbering

    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load configuration using file management API.
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            Configuration dictionary
        """
        if not config_path:
            config_path = Path(__file__).parent / "images.json"
        
        try:
            from ePy_docs.api.file_management import read_json
            return read_json(config_path)
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        except Exception as e:
            raise ValueError(f"Error loading configuration file {config_path}: {e}")

    def process_image(self, path: str, output_dir: str, title: Optional[str] = None, 
                     label: Optional[str] = None, counter: Optional[int] = None) -> str:
        """Process and organize an image with proper captioning.
        
        Args:
            path: Source image path
            output_dir: Base output directory
            title: Image title/caption
            label: Optional custom label for cross-referencing
            counter: Figure counter for numbering
            
        Returns:
            Processed image path with caption
        """
        if not os.path.exists(path):
            raise FileNotFoundError(f"Image file not found: {path}")

        if not self.validate_image_format(path):
            raise ValueError(f"Invalid image format: {path}")

        dest_path = self._organize_image(path, output_dir)
        caption = self._format_caption(title, counter)
        
        return self._create_image_reference(dest_path, caption, label)

    def _organize_image(self, path: str, output_dir: str) -> str:
        """Organize image into figures directory.
        
        Args:
            path: Source image path
            output_dir: Base output directory
            
        Returns:
            Organized image path
        """
        dest_dir = Path(output_dir) / "figures"
        dest_dir.mkdir(parents=True, exist_ok=True)
        
        dest_path = dest_dir / Path(path).name
        if path != str(dest_path):
            shutil.copy2(path, dest_path)
        
        return str(dest_path)

    def _format_caption(self, title: Optional[str], counter: Optional[int] = None) -> str:
        """Format image caption based on configuration.
        
        Args:
            title: Image title/caption
            counter: Figure counter for numbering
            
        Returns:
            Formatted caption
        """
        if not title:
            # Use figure_no_title_format for auto-generated figure labels
            if counter:
                return self.config["pagination"]["figure_no_title_format"].format(
                    counter=counter
                )
            return ""

        # Use figure_title_format when there's a title/caption
        return self.config["pagination"]["figure_title_format"].format(
            title=title
        )

    def _create_image_reference(self, path: str, caption: str, label: Optional[str] = None) -> str:
        """Create a cross-referenced image with caption.
        
        Args:
            path: Image path
            caption: Image caption
            label: Optional custom label for cross-referencing
            
        Returns:
            Image reference with caption
        """
        rel_path = self.get_relative_path(path, os.path.dirname(path))
        
        if self.config["cross_referencing"]["quarto_syntax"]:
            if label:
                fig_label = label
            else:
                # Generate automatic label if auto_numbering is enabled
                if self.config["cross_referencing"]["auto_numbering"]:
                    counter = getattr(self, '_counter', 1)
                    self._counter = counter + 1
                    prefix = self.config["cross_referencing"]["label_prefix"]
                    fig_label = f"#{prefix}{counter}"
                else:
                    fig_label = ""
            
            if caption and fig_label:
                return f"![{caption}]({rel_path}){{{fig_label}}}"
            elif caption:
                return f"![{caption}]({rel_path})"
            elif fig_label:
                return f"![]({rel_path}){{{fig_label}}}"
            else:
                return f"![]({rel_path})"
        
        # Non-Quarto syntax
        if caption:
            return f"![]({rel_path})\n*{caption}*"
        return f"![]({rel_path})"

    @staticmethod
    def get_relative_path(img_path: str, base_dir: str) -> str:
        """Get relative path for cross-platform compatibility.
        
        Args:
            img_path: Absolute image path
            base_dir: Base directory
            
        Returns:
            Relative path with forward slashes
        """
        return os.path.relpath(img_path, base_dir).replace('\\', '/')
    
    @staticmethod
    def get_quarto_relative_path(img_path: str, output_dir: str) -> str:
        """Get relative path compatible with Quarto rendering.
        
        When the QMD file is in a different directory than the images,
        we need to calculate the path from the QMD file location to the image.
        
        Args:
            img_path: Absolute image path
            output_dir: Directory where the QMD file will be located
            
        Returns:
            Relative path with forward slashes for Quarto compatibility
        """
        # Calculate path from output_dir (where QMD is) to the image
        rel_path = os.path.relpath(img_path, output_dir).replace('\\', '/')
        return rel_path

    @staticmethod
    def organize_image(path: str, output_dir: str, subfolder: str = "figures") -> str:
        """Organize image into specified subdirectory (static method).
        
        Args:
            path: Source image path
            output_dir: Base output directory
            subfolder: Subdirectory name (default: "figures")
            
        Returns:
            Organized image path
        """
        import shutil
        dest_dir = Path(output_dir) / subfolder
        dest_dir.mkdir(parents=True, exist_ok=True)
        
        dest_path = dest_dir / Path(path).name
        if path != str(dest_path):
            shutil.copy2(path, dest_path)
        
        return str(dest_path)

    @staticmethod
    def validate_image_format(path: str, allowed_formats: Optional[list] = None) -> bool:
        """Validate image format.
        
        Args:
            path: Image file path
            allowed_formats: List of allowed extensions
            
        Returns:
            True if format is valid
        """
        if allowed_formats is None:
            allowed_formats = ['.png', '.jpg', '.jpeg', '.svg', '.pdf', '.webp']
        
        _, ext = os.path.splitext(path.lower())
        return ext in allowed_formats


def display_in_notebook(img_path: str, show_in_notebook: bool = True) -> None:
    """Display image in Jupyter notebook if available."""
    if not show_in_notebook:
        return
    try:
        from IPython.display import Image, display
        from IPython import get_ipython
        from ePy_docs.core.setup import _load_cached_files, _resolve_config_path
        if get_ipython() is not None:
            if os.path.exists(img_path):
                config_path = _resolve_config_path('units')
                units_config = _load_cached_files(config_path)
                image_width = units_config['display']['formatting']['image_display_width']
                display(Image(img_path, width=image_width))
    except (ImportError, Exception):
        # Silently skip display if not in Jupyter or any other error
        pass


def save_plot_image(fig, output_dir: str, figure_counter: int) -> str:
    """Save matplotlib figure using images.json configuration."""
    from ePy_docs.core.setup import _load_cached_files, _resolve_config_path
    
    # Load images configuration - must exist
    config_path = _resolve_config_path('images')
    images_config = _load_cached_files(config_path)
    if 'figures' not in images_config:
        raise ValueError("Figures configuration not found in images.json")
    
    figures_config = images_config['figures']
    
    # Get directory configuration from setup.json as absolute paths
    from ePy_docs.core.setup import get_absolute_output_directories
    
    output_dirs = get_absolute_output_directories()
    figures_dir = output_dirs['figures']
    os.makedirs(figures_dir, exist_ok=True)
    
    # Generate filename from pattern
    filename_pattern = figures_config['filename_pattern']
    img_filename = filename_pattern.format(counter=figure_counter)
    img_path = os.path.join(figures_dir, img_filename)
    
    # Get save configuration
    save_config = figures_config.get('save', {})
    dpi = save_config.get('dpi')
    if not dpi:
        raise ValueError("DPI not configured in images.json figures.save.dpi")
    
    bbox_inches = save_config.get('bbox_inches')
    if not bbox_inches:
        raise ValueError("bbox_inches not configured in images.json figures.save.bbox_inches")
    
    # Save figure
    fig.savefig(img_path, dpi=dpi, bbox_inches=bbox_inches)
    
    return img_path


def format_figure_markdown(img_path: str, figure_counter: int, title: str = None, 
                          caption: str = None, source: str = None) -> str:
    """Format figure markdown using images.json configuration."""
    from ePy_docs.core.setup import _load_cached_files, _resolve_config_path
    
    # Load images configuration - must exist
    config_path = _resolve_config_path('images')
    images_config = _load_cached_files(config_path)
    if 'figures' not in images_config:
        raise ValueError("Figures configuration not found in images.json")
    
    figures_config = images_config['figures']
    
    # Get markdown template
    if 'markdown_template' not in figures_config:
        raise ValueError("Figures markdown template not configured in images.json")
    
    template = figures_config['markdown_template']
    
    # Get relative path for markdown
    relative_path = os.path.relpath(img_path)
    
    # Format the template
    return template.format(
        path=relative_path,
        counter=figure_counter,
        title=title or '',
        caption=caption or '',
        source=source or ''
    )


def copy_and_process_image(path: str, output_dir: str, figure_counter: int) -> str:
    """Copy external image using images.json configuration."""
    from ePy_docs.core.setup import _load_cached_files, _resolve_config_path
    
    # Load images configuration - must exist
    config_path = _resolve_config_path('images')
    images_config = _load_cached_files(config_path)
    if 'figures' not in images_config:
        raise ValueError("Figures configuration not found in images.json")
    
    figures_config = images_config['figures']
    
    # Get directory configuration from setup.json as absolute paths
    from ePy_docs.core.setup import get_absolute_output_directories
    
    output_dirs = get_absolute_output_directories()
    figures_dir = output_dirs['figures']
    os.makedirs(figures_dir, exist_ok=True)
    
    # Get file extension and create new filename
    _, ext = os.path.splitext(path)
    if 'filename_pattern' not in figures_config:
        raise ValueError("Figures filename pattern not configured in images.json")
    
    filename_pattern = figures_config['filename_pattern']
    new_filename = filename_pattern.format(counter=figure_counter) + ext
    dest_path = os.path.join(figures_dir, new_filename)
    
    # Copy file
    import shutil
    shutil.copy2(path, dest_path)
    
    return dest_path


def format_image_markdown(dest_path: str, figure_counter: int, caption: str = None, 
                         width: str = None, alt_text: str = None, align: str = None, 
                         label: str = None, source: str = None, output_dir: str = None) -> tuple:
    """Format image markdown using images.json configuration."""
    from ePy_docs.core.setup import _load_cached_files, _resolve_config_path
    
    # Load images configuration - must exist
    config_path = _resolve_config_path('images')
    images_config = _load_cached_files(config_path)
    
    # Get relative path for markdown using Quarto-compatible path calculation
    rel_path = ImageProcessor.get_quarto_relative_path(dest_path, output_dir) if output_dir else os.path.relpath(dest_path)
    
    # Create figure label
    if label is None:
        if 'cross_referencing' not in images_config:
            raise ValueError("Cross referencing configuration not found in images.json")
        
        cross_ref_config = images_config['cross_referencing']
        if 'label_format' not in cross_ref_config or 'label_prefix' not in cross_ref_config:
            raise ValueError("Cross referencing format not configured in images.json")
            
        label_format = cross_ref_config['label_format']
        label_prefix = cross_ref_config['label_prefix']
        figure_id = label_format.format(prefix=label_prefix, counter=figure_counter)
    else:
        if not label.startswith('fig-'):
            figure_id = f"fig-{label}"
        else:
            figure_id = label
    
    # Format caption
    if 'pagination' not in images_config:
        raise ValueError("Pagination configuration not found in images.json")
        
    pagination_config = images_config['pagination']
    
    if caption:
        if 'figure_title_format' not in pagination_config:
            raise ValueError("Figure title format not configured in images.json")
        fig_caption = pagination_config['figure_title_format'].format(title=caption)
    else:
        if 'figure_no_title_format' not in pagination_config:
            raise ValueError("Figure no title format not configured in images.json")
        fig_caption = pagination_config['figure_no_title_format']
    
    # Add source if provided
    if source:
        if fig_caption:
            fig_caption = f"{fig_caption} ({source})"
        else:
            fig_caption = f"({source})"
    
    # Use alt_text if provided
    if alt_text:
        fig_caption = alt_text
    
    # Build attributes
    attributes = [f'#{figure_id}']
    if width:
        attributes.append(f'fig-width="{width}"')
    if align:
        attributes.append(f'fig-align="{align}"')
    
    # Create markdown
    img_markdown = f"\n\n![{fig_caption}]({rel_path}){{{' '.join(attributes)}}}\n\n"
    
    return img_markdown, figure_id
