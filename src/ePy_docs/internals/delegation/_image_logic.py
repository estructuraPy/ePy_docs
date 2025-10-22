"""
Image Processing Logic
======================

Handles image-related business logic.
"""

from ePy_docs.internals.delegation._common import tempfile


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
    import matplotlib.pyplot as plt
    
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
        fig.savefig(
            temp_file.name,
            format='png',
            dpi=300,
            bbox_inches='tight'
        )
    
    return temp_file.name
