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

# ========================================
# CRITICAL: Configure matplotlib FIRST
# ========================================
# This MUST happen before ANY matplotlib import to avoid font warnings
try:
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend
    from matplotlib import rcParams
    from pathlib import Path
    import matplotlib.font_manager as fm
    import logging
    
    # Suppress matplotlib font warnings
    logging.getLogger('matplotlib.font_manager').setLevel(logging.ERROR)
    
    # Set safe defaults with proper fallback - NO DejaVu Sans to avoid errors if not installed
    rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'sans-serif']
    rcParams['font.family'] = 'sans-serif'
    rcParams['font.size'] = 10
    rcParams['axes.unicode_minus'] = False
    rcParams['mathtext.fallback'] = 'cm'  # Enable fallback for math text
    
    # CRITICAL: Enable default font fallback in matplotlib
    # This prevents "fallback to the default font was disabled" errors
    # MONKEY-PATCH: Wrap matplotlib's _findfont_cached to prevent fallback disabling
    import matplotlib.font_manager as _fm
    from types import MethodType
    
    if hasattr(_fm, 'fontManager') and hasattr(_fm.fontManager, '_findfont_cached'):
        # Patch _findfont_cached which is where fallback_to_default gets set to False
        _original_findfont_cached = _fm.FontManager._findfont_cached
        
        def _safe_findfont_cached(self, *args, **kwargs):
            """Wrapper that prevents disabling fallback."""
            try:
                return _original_findfont_cached(self, *args, **kwargs)
            except (ValueError, RuntimeError) as e:
                # If it fails, return a valid font path
                if "fallback to the default font was disabled" in str(e):
                    # Return Arial or first available font
                    for font_entry in self.ttflist:
                        if 'arial' in font_entry.name.lower() and font_entry.fname:
                            from pathlib import Path
                            if Path(font_entry.fname).is_file():
                                return font_entry.fname
                    # Return first valid font
                    for font_entry in self.ttflist:
                        if font_entry.fname:
                            from pathlib import Path
                            if Path(font_entry.fname).is_file():
                                return font_entry.fname
                raise
        
        _fm.fontManager._findfont_cached = MethodType(_safe_findfont_cached, _fm.fontManager)
    
    # Register Arial Narrow from package if available
    package_root = Path(__file__).parent
    arial_narrow_path = package_root / 'config' / 'assets' / 'fonts' / 'arial_narrow.TTF'
    if arial_narrow_path.exists():
        fm.fontManager.addfont(str(arial_narrow_path))
except Exception:
    pass  # Silently fail if matplotlib not available
# ========================================

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


