"""
Image Processing Logic
======================

Handles image-related business logic.
"""

import tempfile


def parse_image_width(width: str) -> int:
    """
    Parse width string to extract pixel value.
    
    Args:
        width: Width string (e.g., "500px")
        
    Returns:
        int: Width in pixels, or None if not parseable
    """
    if width and width.endswith('px'):
        try:
            return int(width[:-2])
        except ValueError:
            return None
    return None


def save_plot_to_temp(fig) -> str:
    """
    Save a matplotlib figure to a temporary file.
    
    Args:
        fig: Matplotlib figure object
        
    Returns:
        str: Path to temporary file
    """
    from ePy_files.saver import save_matplotlib_figure
    
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
        temp_path = save_matplotlib_figure(
            fig,
            temp_file.name,
            format='png',
            dpi=300,
            bbox_inches='tight'
        )
    
    return temp_path
