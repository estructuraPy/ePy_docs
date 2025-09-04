"""Test 001: Creative layout background color verification.

Tests whether the creative layout correctly applies black background
instead of appearing white.
"""
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ePy_docs.components.colors import get_colors_config, get_color
from ePy_docs.components.pages import set_current_layout, get_current_layout


def test_creative_background_color():
    """Test that creative layout returns black background color."""
    
    # Set creative layout
    set_current_layout("creative")
    current = get_current_layout()
    print(f"Current layout: {current}")
    
    # Get colors configuration
    colors_config = get_colors_config(sync_files=False)
    
    # Get creative layout configuration
    creative_config = colors_config.get('layout_styles', {}).get('creative', {})
    typography = creative_config.get('typography', {})
    background_config = typography.get('background_color', {})
    
    print(f"Creative background config: {background_config}")
    
    # Get background color using get_color
    background_color = get_color('layout_styles.creative.typography.background_color')
    print(f"Background color returned: {background_color}")
    
    # Verify it's black [0, 0, 0]
    expected_black = [0, 0, 0]
    
    print(f"Expected: {expected_black}")
    print(f"Actual: {background_color}")
    print(f"Colors match: {background_color == expected_black}")
    
    # Test direct palette access
    palette_name = background_config.get('palette', '')
    tone = background_config.get('tone', '')
    print(f"Palette: {palette_name}, Tone: {tone}")
    
    if palette_name and tone:
        direct_color = get_color(f'{palette_name}.{tone}')
        print(f"Direct palette color: {direct_color}")
    
    return background_color == expected_black


if __name__ == "__main__":
    result = test_creative_background_color()
    print(f"\nTest result: {'PASS' if result else 'FAIL'}")
