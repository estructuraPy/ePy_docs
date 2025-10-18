"""
REINO IMAGES - Soberanía Absoluta de Imágenes

Dimensión Setup: Caché centralizado por medio de _load_cached_files
Dimensión Apariencia: Organización por layout_styles
Dimensión Transparencia: Sin backward compatibility, sin fallbacks
"""

from typing import Dict, Any, Tuple, Optional, Union
import os
import shutil
import re
# Import from internal data module
from ePy_docs.internals.data_processing._data import load_cached_files, _safe_get_nested

from ePy_docs.config.setup import _resolve_config_path

def get_images_config() -> Dict[str, Any]:
    """Sucursal de la secretaría de comercio para recursos de imágenes."""
    config_path = _resolve_config_path('components/images')
    return load_cached_files(config_path)

def _copy_image_to_output_directory(img_path: str, figure_counter: int, document_type: str = "report") -> str:
    """Copy image to appropriate output directory with sequential naming based on document_type - IMAGES reino sovereignty."""
    if not img_path or not os.path.exists(img_path):
        # If image doesn't exist, return original path (processed for LaTeX compatibility)
        return process_image_path(img_path)
    
    from pathlib import Path
    from ePy_docs.config.setup import get_absolute_output_directories
    
    # Get the appropriate output directory for this document type
    output_dirs = get_absolute_output_directories(document_type=document_type)
    figures_dir = output_dirs['figures']
    
    # Ensure the figures directory exists
    os.makedirs(figures_dir, exist_ok=True)
    
    # Get the original extension
    path_obj = Path(img_path)
    extension = path_obj.suffix
    
    # Generate sequential filename: figure_1.png, figure_2.jpg, etc.
    sequential_filename = f"figure_{figure_counter}{extension}"
    
    # Create destination path with sequential name
    dest_path = os.path.join(figures_dir, sequential_filename)
    
    # Copy the image (always copy to ensure correct sequential naming)
    shutil.copy2(img_path, dest_path)
    
    # Return the processed path for LaTeX compatibility
    return process_image_path(dest_path)



def add_image_to_content(
    img_path: str, 
    title: str = None, 
    caption: str = None, 
    image_id: str = None, 
    fig_width: int = None,
    alt_text: str = None,
    responsive: bool = True,
    document_type: str = "report",
    figure_counter: int = 0
) -> tuple[str, int]:
    """Generate image markdown with full configuration - IMAGES reino sovereignty.
    
    Returns:
        Tuple of (markdown_content, updated_figure_counter)
    """
    config = get_images_config()
    
    # Increment counter for this image
    figure_counter += 1
    
    # Copy image to appropriate directory with sequential naming
    processed_path = _copy_image_to_output_directory(img_path, figure_counter, document_type)
    
    # Build image attributes
    attributes = []
    
    if image_id:
        attributes.append(f'#{image_id}')
    
    if fig_width:
        attributes.append(f'fig-width={fig_width}')
    
    # responsive=true is only for HTML output, causes issues in LaTeX
    # Only add responsive attribute for HTML-compatible formats
    if responsive:
        # TODO: Could add context detection here to only include for HTML output
        # For now, commenting out to prevent LaTeX issues
        # attributes.append('responsive=true')
        pass
    
    # Create markdown content - start with blank lines for separation
    markdown_parts = []
    
    if title:
        markdown_parts.append(f"### {title}\n")
    
    # Image markdown with attributes
    if attributes:
        attr_string = ' {' + ' '.join(attributes) + '}'
        image_markdown = f"![{alt_text or caption or ''}]({processed_path}){attr_string}"
    else:
        image_markdown = f"![{alt_text or caption or ''}]({processed_path})"
    
    markdown_parts.append(image_markdown)
    
    # Caption is already in the image syntax ![caption](path), no need to repeat it
    # Removed: if caption and not title: markdown_parts.append(f"\n*{caption}*")
    
    # Add blank line before to ensure separation from previous content
    return "\n\n" + "\n".join(markdown_parts) + "\n\n", figure_counter

def add_plot_to_content(
    img_path: str,
    title: str = None,
    caption: str = None,
    source: str = None
) -> str:
    """Generate plot markdown with proper formatting - IMAGES reino sovereignty."""
    config = get_images_config()
    
    # Process image path
    processed_path = process_image_path(img_path)
    
    # Build plot content
    markdown_parts = []
    
    if title:
        markdown_parts.append(f"### {title}\n")
    
    # Plot image
    plot_markdown = f"![{caption or title or 'Plot'}]({processed_path})"
    markdown_parts.append(plot_markdown)
    
    # Caption and source
    caption_parts = []
    if caption:
        caption_parts.append(caption)
    if source:
        caption_parts.append(f"Source: {source}")
    
    if caption_parts:
        markdown_parts.append(f"\n*{' - '.join(caption_parts)}*")
    
    return "\n".join(markdown_parts) + "\n\n"

def process_image_path(img_path: str) -> str:
    """Process and normalize image path for markdown output."""
    if not img_path:
        return ""
    
    from pathlib import Path
    
    # For LaTeX reliability, always use absolute paths when files exist
    path_obj = Path(img_path)
    
    # If it's already absolute and exists, use it
    if path_obj.is_absolute() and path_obj.exists():
        img_path = str(path_obj)
    # If it's relative and exists, convert to absolute for LaTeX reliability
    elif not path_obj.is_absolute() and path_obj.exists():
        img_path = str(path_obj.resolve())
    # If file doesn't exist, keep original path (might be generated later)
    else:
        # Try to convert relative paths that don't exist to absolute in case they will exist
        if not path_obj.is_absolute():
            try:
                img_path = str(path_obj.resolve())
            except:
                pass
    
    # Normalize path separators for cross-platform compatibility
    img_path = img_path.replace('\\', '/')
    
    return img_path

def fix_image_paths_in_imported_content(content: str, source_file_path: str, 
                                      output_dir: str, figure_counter: int = 0,
                                      document_type: str = "report") -> tuple[str, int]:
    """Fix image paths in imported content - IMAGES reino sovereignty.
    
    This function processes imported markdown/quarto files that contain image references
    with relative paths, copying images and updating paths for the current context.
    
    Args:
        content: The content to process
        source_file_path: Path of the source file being imported
        output_dir: Output directory where figures should be copied
        figure_counter: Current figure counter (will be incremented)
        document_type: Document type for output directory structure
        
    Returns:
        Tuple of (processed_content, updated_figure_counter)
    """
    import re
    from ePy_docs.config.setup import get_absolute_output_directories
    
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
            rel_path = process_image_path(dest_path)
            
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
