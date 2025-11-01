"""
Image Processing Module

Handles image and plot operations for document generation.
"""

from typing import Tuple, List, Optional
from pathlib import Path
import shutil


def parse_image_width(width: str = None) -> str:
    """
    Parse and validate image width specification.
    
    Args:
        width: Width specification (e.g., '50%', '300px', None)
        
    Returns:
        Validated width string
    """
    if width is None:
        return '100%'
    
    # Simple validation
    if isinstance(width, str):
        if width.endswith('%') or width.endswith('px') or width.endswith('em'):
            return width
    
    return str(width) if width else '100%'


def add_image_content(
    path: str,
    caption: str = None,
    width: str = None,
    alt_text: str = None,
    responsive: bool = True,
    document_type: str = 'report',
    figure_counter: int = 1,
    output_dir: Optional[str] = None,
    show_figure: bool = True,
    **kwargs
) -> Tuple[str, int, List]:
    """
    Generate image markdown with standardized naming and return new counter.
    
    This function:
    1. Copies the source image to results/report/figures/ directory
    2. Renames it with consecutive numbering (figure_1.png, figure_2.png, etc.)
    3. Generates markdown with proper figure numbering
    4. Optionally displays the image in Jupyter notebooks
    
    Args:
        path: Source image file path
        caption: Optional caption
        width: Optional width
        alt_text: Optional alt text
        responsive: Whether image should be responsive
        document_type: Document type
        figure_counter: Current figure counter
        output_dir: Optional output directory (if None, uses default figures dir)
        show_figure: If True, display the image in Jupyter notebooks
        **kwargs: Additional options
        
    Returns:
        Tuple of (markdown, new_counter, generated_images)
    """
    # Get output directory for figures
    if output_dir is None:
        from ePy_docs.core._config import get_absolute_output_directories
        output_dirs = get_absolute_output_directories(document_type=document_type)
        # Use figures subdirectory
        output_dir = Path(output_dirs['report']) / 'figures'
    else:
        output_dir = Path(output_dir)
    
    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate standardized filename
    source_path = Path(path)
    extension = source_path.suffix or '.png'
    new_filename = f"figure_{figure_counter}{extension}"
    dest_path = output_dir / new_filename
    
    # Copy image to destination with new name
    try:
        shutil.copy2(source_path, dest_path)
        img_path = str(dest_path)
    except (FileNotFoundError, PermissionError) as e:
        # If copy fails, use original path
        img_path = path
    
    # Display image in notebook if requested
    if show_figure:
        try:
            from IPython.display import Image, display
            display(Image(filename=img_path))
        except (ImportError, NameError):
            pass  # Not in Jupyter environment
    
    # Build markdown
    fig_num = f"Figura {figure_counter}"
    
    # Parse width
    fig_width = parse_image_width(width)
    
    # Build image markdown
    alt = alt_text or caption or "Image"
    markdown_parts = []
    
    if caption:
        markdown_parts.append(f"**{fig_num}:** {caption}\n\n")
    
    # Image syntax - use relative path from output directory
    markdown_parts.append(f"![{alt}]({img_path})")
    
    # Add width if specified
    if fig_width and fig_width != '100%':
        markdown_parts.append(f"{{width={fig_width}}}")
    
    # Add figure ID for cross-references
    figure_id = f"fig-{figure_counter}"
    markdown_parts.append(f"{{#{figure_id}}}")
    
    markdown_parts.append("\n\n")
    
    markdown = ''.join(markdown_parts)
    
    # Return the same counter (increment handled by writers.py)
    return markdown, figure_counter, [str(dest_path)]


def save_plot_to_output(fig, figure_counter: int, output_dir: Optional[str] = None, 
                        document_type: str = 'report') -> str:
    """
    Save matplotlib figure to output directory with standardized naming.
    
    Args:
        fig: Matplotlib figure object
        figure_counter: Current figure counter
        output_dir: Optional output directory (if None, uses default figures dir)
        document_type: Document type
        
    Returns:
        Path to saved file
    """
    # Get output directory for figures
    if output_dir is None:
        from ePy_docs.core._config import get_absolute_output_directories
        output_dirs = get_absolute_output_directories(document_type=document_type)
        # Use figures subdirectory
        output_dir = Path(output_dirs['report']) / 'figures'
    else:
        output_dir = Path(output_dir)
    
    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate standardized filename
    filename = f"figure_{figure_counter}.png"
    output_path = output_dir / filename
    
    # Save figure
    fig.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    
    # Close the figure to prevent duplicate display in notebooks
    import matplotlib.pyplot as plt
    plt.close(fig)
    
    return str(output_path)


def add_plot_content(
    img_path: str = None,
    fig = None,
    title: str = None,
    caption: str = None,
    figure_counter: int = 1,
    output_dir: Optional[str] = None,
    document_type: str = 'report',
    show_figure: bool = True,
    **kwargs
) -> Tuple[str, int]:
    """
    Generate plot markdown with standardized naming and return new counter.
    
    This function:
    1. Saves the matplotlib figure to results/report/figures/ directory
    2. Names it with consecutive numbering (figure_1.png, figure_2.png, etc.)
    3. Generates markdown with proper figure numbering
    4. Optionally displays the figure in Jupyter notebooks
    
    Args:
        img_path: Path to existing image file (optional, use if fig is None)
        fig: Matplotlib figure object (optional, use if img_path is None)
        title: Optional title
        caption: Optional caption
        figure_counter: Current figure counter
        output_dir: Optional output directory
        document_type: Document type
        show_figure: If True, display the figure in Jupyter notebooks
        **kwargs: Additional options
        
    Returns:
        Tuple of (markdown, new_counter)
    """
    # Display figure in notebook if requested (BEFORE saving/closing)
    if show_figure and fig is not None:
        try:
            from IPython.display import display
            display(fig)
        except (ImportError, NameError):
            pass  # Not in Jupyter environment
    
    # Save figure if provided, otherwise use existing path
    if fig is not None:
        final_path = save_plot_to_output(fig, figure_counter, output_dir, document_type)
    elif img_path is not None:
        # Copy existing image to standardized location
        from ePy_docs.core._config import get_absolute_output_directories
        if output_dir is None:
            output_dirs = get_absolute_output_directories(document_type=document_type)
            output_dir = Path(output_dirs['report']) / 'figures'
        else:
            output_dir = Path(output_dir)
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        source_path = Path(img_path)
        extension = source_path.suffix or '.png'
        new_filename = f"figure_{figure_counter}{extension}"
        dest_path = output_dir / new_filename
        
        try:
            shutil.copy2(source_path, dest_path)
            final_path = str(dest_path)
        except (FileNotFoundError, PermissionError):
            final_path = img_path
    else:
        raise ValueError("Either img_path or fig must be provided")
    
    # Build markdown
    markdown_parts = []
    
    if title:
        markdown_parts.append(f"### {title}\n\n")
    
    fig_num = f"Figura {figure_counter}"
    
    if caption:
        markdown_parts.append(f"**{fig_num}:** {caption}\n\n")
    
    # Image syntax with figure ID
    figure_id = f"fig-{figure_counter}"
    markdown_parts.append(f"![]({final_path}){{#{figure_id}}}\n\n")
    
    markdown = ''.join(markdown_parts)
    
    # Return the same counter (increment handled by writers.py)
    return markdown, figure_counter
