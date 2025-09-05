"""
REINO IMAGES - Soberanía Absoluta de Imágenes

Dimensión Setup: Caché centralizado por medio de _load_cached_files
Dimensión Apariencia: Organización por layout_styles
Dimensión Transparencia: Sin backward compatibility, sin fallbacks
"""

from typing import Dict, Any, Tuple
import os
import shutil
from ePy_docs.components.setup import _load_cached_files, _resolve_config_path

def _get_images_config(sync_files: bool = False) -> Dict[str, Any]:
    """Sucursal de la secretaría de comercio para recursos de imágenes.
    
    Args:
        sync_files: Control de sincronización de archivos
        
    Returns:
        Configuración completa de imágenes
        
    Raises:
        RuntimeError: Si la carga falla
        
    Assumptions:
        El archivo images.json existe en la ubicación resuelta
    """
    try:
        config_path = _resolve_config_path('components/images', sync_files)
        config = _load_cached_files(config_path, sync_files)
        
        required_keys = ['layout_styles']
        for key in required_keys:
            if key not in config:
                raise KeyError(f"Missing required configuration key: {key}")
        
        return config
        
    except Exception as e:
        raise RuntimeError(f"Failed to load images configuration: {e}") from e

def get_images_config(sync_files: bool = False) -> Dict[str, Any]:
    """Única función pública para acceso a recursos de imágenes.
    
    Comercio oficial del Reino IMAGES.
    
    Args:
        sync_files: Control de sincronización de archivos
        
    Returns:
        Configuración completa de imágenes
        
    Raises:
        RuntimeError: Si la carga falla
        
    Assumptions:
        El sistema de layout_styles está correctamente configurado
    """
    return _get_images_config(sync_files)

def copy_and_process_image(image_path: str, output_dir: str, figure_counter: int) -> str:
    """Copy and process image for report inclusion.
    
    Compatibility function for ReportWriter. Uses pure kingdom architecture internally.
    
    Args:
        image_path: Path to source image
        output_dir: Output directory for processed image
        figure_counter: Figure counter for naming
        
    Returns:
        Path to processed image
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")
    
    # Create figures directory
    figures_dir = os.path.join(output_dir, 'figures')
    os.makedirs(figures_dir, exist_ok=True)
    
    # Generate filename
    filename = f"figure_{figure_counter:03d}{os.path.splitext(image_path)[1]}"
    dest_path = os.path.join(figures_dir, filename)
    
    # Copy image
    shutil.copy2(image_path, dest_path)
    
    # Return destination path
    return dest_path

def format_image_markdown(dest_path: str, figure_counter: int, caption: str = None, 
                         width: str = None, alt_text: str = None, align: str = None, 
                         label: str = None, source: str = None, output_dir: str = None) -> Tuple[str, str]:
    """Format image as markdown.
    
    Compatibility function for ReportWriter. Uses pure kingdom architecture internally.
    
    Args:
        dest_path: Path to processed image
        figure_counter: Figure counter for ID generation
        caption: Image caption
        width: Image width specification
        alt_text: Alternative text
        align: Image alignment
        label: Figure label for cross-references
        source: Source attribution
        output_dir: Output directory for relative path calculation
        
    Returns:
        Tuple of (formatted_markdown, figure_id)
    """
    # Generate figure ID
    figure_id = f"fig-{figure_counter:03d}"
    if label:
        figure_id = f"fig-{label}"
    
    # Calculate relative path for markdown
    if output_dir and os.path.isabs(dest_path):
        rel_path = os.path.relpath(dest_path, output_dir).replace('\\', '/')
    else:
        rel_path = dest_path
    
    # Use alt_text as fallback for caption if not provided
    display_text = alt_text or caption or "Image"
    
    # Build markdown image syntax
    markdown = f"![{display_text}]({rel_path})"
    
    # Add attributes if specified
    attributes = []
    if width:
        attributes.append(f"width={width}")
    if align:
        attributes.append(f"fig-align={align}")
    
    # Always add figure ID for cross-references
    attributes.append(f"#{figure_id}")
    
    if attributes:
        markdown += "{" + " ".join(attributes) + "}"
    
    # Add caption if provided and different from alt_text
    if caption and caption != alt_text:
        caption_text = caption
        if source:
            caption_text += f" {source}"
        markdown += f"\n\n: {caption_text}"
    elif source:
        markdown += f"\n\n: {source}"
    
    return markdown, figure_id


class ImageProcessor:
    """Compatibility class for legacy ImageProcessor functionality.
    
    Maintains kingdom architecture while providing backward compatibility.
    """
    
    @staticmethod
    def organize_image(image_path: str, base_dir: str, figures_subdir: str) -> str:
        """Organize image into appropriate subdirectory.
        
        Args:
            image_path: Source image path
            base_dir: Base output directory
            figures_subdir: Figures subdirectory name
            
        Returns:
            Path to organized image
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        # Create figures directory
        figures_dir = os.path.join(base_dir, figures_subdir)
        os.makedirs(figures_dir, exist_ok=True)
        
        # Generate destination filename
        filename = os.path.basename(image_path)
        dest_path = os.path.join(figures_dir, filename)
        
        # Copy image if not already in target location
        if os.path.abspath(image_path) != os.path.abspath(dest_path):
            shutil.copy2(image_path, dest_path)
        
        return dest_path
    
    @staticmethod
    def get_quarto_relative_path(image_path: str, output_dir: str) -> str:
        """Get Quarto-compatible relative path.
        
        Args:
            image_path: Absolute path to image
            output_dir: Output directory for relative calculation
            
        Returns:
            Relative path using forward slashes
        """
        if os.path.isabs(image_path) and output_dir:
            rel_path = os.path.relpath(image_path, output_dir)
            # Convert to forward slashes for cross-platform compatibility
            return rel_path.replace('\\', '/')
        return image_path

def display_in_notebook(image_path: str, show: bool = True, width: int = None) -> None:
    """Official display function for images and tables in Jupyter notebooks.
    
    Respects DIMENSIÓN TRANSPARENCIA - no fallbacks, no verbose output.
    Uses official commercial office for configuration access.
    
    Args:
        image_path: Path to image file to display.
        show: Whether to display the image.
        width: Optional width override for display.
    """
    if not show or not os.path.exists(image_path):
        return
    
    try:
        from IPython.display import Image, display
        from IPython import get_ipython
        
        if get_ipython() is not None:
            # Use official commercial office for configuration
            config = get_images_config(sync_files=False)
            display_width = width or config.get('display', {}).get('notebook_width', 600)
            display(Image(image_path, width=display_width))
    except (ImportError, Exception):
        # DIMENSIÓN TRANSPARENCIA: Silent failure, no verbose errors
        pass
