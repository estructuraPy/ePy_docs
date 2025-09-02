"""
MATH KINGDOM - Mathematical Content Processing
Handles mathematical expressions, equations, and delegated content from text.py
Following Lord's decrees: NO hardcoded, NO fallbacks, clean code
"""

from typing import Dict, Any, Optional
from ePy_docs.core.setup import _load_cached_files, _resolve_config_path

def _load_math_config(sync_files: bool = False) -> Dict[str, Any]:
    """Load math configuration from centralized math.json."""
    config_path = _resolve_config_path('components/math', sync_files)
    config = _load_cached_files(config_path, sync_files)
    
    if 'mathematical_processing' not in config:
        raise KeyError("MATH KINGDOM FAILURE: 'mathematical_processing' missing from configuration")
    
    return config

def load_math_config(sync_files: bool = False) -> Dict[str, Any]:
    """Public function to load math configuration - used by other components."""
    return _load_math_config(sync_files)

def process_mathematical_text(text: str, layout_name: str, sync_files: bool) -> str:
    """Process text containing mathematical content - delegated from text.py."""
    config = _load_math_config(sync_files)
    
    if 'mathematical_processing' not in config:
        raise KeyError("MATH KINGDOM FAILURE: 'mathematical_processing' missing from math configuration")
    
    math_config = config['mathematical_processing']
    
    # For now, return the text as-is since this is a delegation placeholder
    # Future implementation would handle LaTeX, MathML, etc.
    return text

class MathProcessor:
    """Mathematical content processor."""
    
    def __init__(self, layout_name: str = 'academic', sync_files: bool = False):
        self.layout_name = layout_name
        self.sync_files = sync_files
        self.config = _load_math_config(sync_files)
    
    def process_equation(self, equation: str) -> str:
        """Process mathematical equation."""
        return process_mathematical_text(equation, self.layout_name, self.sync_files)
    
    def format_formula(self, formula: str) -> str:
        """Format mathematical formula.""" 
        return process_mathematical_text(formula, self.layout_name, self.sync_files)

# Export for compatibility
__all__ = ['MathProcessor', 'process_mathematical_text', 'load_math_config']
