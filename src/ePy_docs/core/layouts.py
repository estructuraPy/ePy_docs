"""
Global layout management for ePy_docs.

This module provides global layout state management to avoid circular imports
and ensure consistent layout application throughout the system.
"""

# Global layout configuration - set by quick_setup()
_CURRENT_LAYOUT = None

def set_current_layout(layout_name: str) -> None:
    """Set the current layout globally."""
    global _CURRENT_LAYOUT
    _CURRENT_LAYOUT = layout_name

def get_current_layout() -> str:
    """Get the current layout. Required - no fallbacks."""
    global _CURRENT_LAYOUT
    if _CURRENT_LAYOUT is None:
        raise RuntimeError("No layout set. Call quick_setup() first with layout_name parameter.")
    return _CURRENT_LAYOUT