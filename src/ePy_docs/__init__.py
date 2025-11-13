"""ePy_docs - Engineering document generation library.

Public API:
- DocumentWriter: Main class for document generation (unified API)
- setup_matplotlib_fonts: Configure matplotlib fonts for a layout
- apply_fonts_to_plot: Apply fonts directly to plot elements
- apply_fonts_to_figure: Apply fonts directly to figure elements

Internal structure (not exposed):
- writers.py: Core API implementation (pure delegation)
- config/: Configuration loaders
- internals/: Implementation logic (styling, generation, data processing, formatting)
- utils/: Internal utilities (validation)
- resources/: Configuration files (.epyson)
"""

__version__ = "0.2.0"

# External libraries validation - Units now handled by user
# ePy_units is no longer required

# Public API - unified DocumentWriter 
from ePy_docs.writers import DocumentWriter

# Note: Font utilities now available through DocumentWriter methods
# setup_matplotlib_fonts, apply_fonts_to_plot, apply_fonts_to_figure
# are accessible via DocumentWriter instance methods

__all__ = [
    'DocumentWriter',
]

