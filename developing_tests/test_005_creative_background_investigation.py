"""Test 005: Creative layout black background color investigation.

Final investigation to determine why the creative layout background
appears white instead of black in generated documents.
"""
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def test_color_resolution_chain():
    """Test the complete color resolution chain for creative background."""
    
    print("=== CREATIVE LAYOUT BACKGROUND COLOR INVESTIGATION ===\n")
    
    # Test 1: Direct color configuration
    print("1. Testing direct color configuration:")
    from ePy_docs.components.colors import get_colors_config, get_color
    
    colors_config = get_colors_config(sync_files=False)
    creative_config = colors_config.get('layout_styles', {}).get('creative', {})
    background_config = creative_config.get('typography', {}).get('background_color', {})
    
    print(f"   Background config: {background_config}")
    
    palette_name = background_config.get('palette')
    tone = background_config.get('tone')
    print(f"   Palette: {palette_name}, Tone: {tone}")
    
    if palette_name and tone:
        direct_color = get_color(f'{palette_name}.{tone}')
        print(f"   Direct color value: {direct_color}")
    
    # Test 2: Layout style resolution
    print(f"\n2. Testing layout style resolution:")
    try:
        layout_background = get_color('layout_styles.creative.typography.background_color')
        print(f"   Layout background: {layout_background}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: Check neutrals palette
    print(f"\n3. Testing neutrals palette:")
    neutrals = colors_config.get('palettes', {}).get('neutrals', {})
    print(f"   Neutrals palette: {neutrals}")
    black_value = neutrals.get('black')
    print(f"   Black value: {black_value}")
    
    # Test 4: Layout setting
    print(f"\n4. Testing current layout:")
    from ePy_docs.components.pages import get_current_layout, set_current_layout
    
    current = get_current_layout()
    print(f"   Current layout: {current}")
    
    if current != 'creative':
        set_current_layout('creative')
        print(f"   Set to creative, now: {get_current_layout()}")
    
    # Test 5: PDF/Document generation context  
    print(f"\n5. Testing document generation context:")
    try:
        from ePy_docs.components.styler import DocumentStyler
        styler = DocumentStyler()
        print(f"   DocumentStyler created successfully")
        
        # Try to get background style
        bg_style = styler.get_background_style()
        print(f"   Background style: {bg_style}")
    except Exception as e:
        print(f"   ❌ Error getting background style: {e}")
    
    # Test 6: Check if there are overrides
    print(f"\n6. Testing for potential overrides:")
    try:
        from ePy_docs.components.pages import get_layout_config
        layout_config = get_layout_config('creative')
        print(f"   Layout config keys: {list(layout_config.keys())}")
        
        if 'background' in layout_config:
            print(f"   Background override: {layout_config['background']}")
    except Exception as e:
        print(f"   ❌ Error getting layout config: {e}")
    
    return True


def create_color_test_evidence():
    """Create a simple color test file to verify colors."""
    
    print(f"\n=== CREATING COLOR TEST EVIDENCE ===")
    
    from ePy_docs.components.colors import get_colors_config, get_color
    
    # Create a simple HTML file to test colors visually
    colors_config = get_colors_config(sync_files=False)
    
    html_content = """<!DOCTYPE html>
<html>
<head>
    <title>Color Test Evidence</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .color-box { 
            width: 200px; 
            height: 100px; 
            margin: 10px 0; 
            border: 2px solid #333;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <h1>ePy_docs Color Test Evidence</h1>
    <h2>Creative Layout Background Color Test</h2>
    
"""
    
    try:
        # Test creative background color
        creative_bg = get_color('layout_styles.creative.typography.background_color')
        bg_rgb = f"rgb({creative_bg[0]}, {creative_bg[1]}, {creative_bg[2]})"
        
        html_content += f"""
    <div class="color-box" style="background-color: {bg_rgb};">
        Creative Background<br>
        {creative_bg} = {bg_rgb}
    </div>
    
    <p>Expected: RGB(0, 0, 0) = Pure Black</p>
    <p>Actual: {creative_bg}</p>
    <p>Match: {'✅ YES' if creative_bg == [0, 0, 0] else '❌ NO'}</p>
        """
        
        # Test neutrals black directly
        black_direct = get_color('neutrals.black')
        black_rgb = f"rgb({black_direct[0]}, {black_direct[1]}, {black_direct[2]})"
        
        html_content += f"""
    <div class="color-box" style="background-color: {black_rgb};">
        Neutrals Black<br>
        {black_direct} = {black_rgb}
    </div>
    
    <p>Neutrals.black: {black_direct}</p>
        """
        
    except Exception as e:
        html_content += f"<p>❌ Error getting colors: {e}</p>"
    
    html_content += """
</body>
</html>
"""
    
    # Save evidence file
    evidence_path = Path(__file__).parent / "evidence_test_005_color_verification.html"
    with open(evidence_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"   ✅ Evidence file created: {evidence_path}")
    print(f"   🔍 Open this file in a browser to visually verify colors")
    
    return evidence_path


if __name__ == "__main__":
    print("🔍 INVESTIGATING CREATIVE BACKGROUND COLOR ISSUE")
    
    test_color_resolution_chain()
    evidence_path = create_color_test_evidence()
    
    print(f"\n=== INVESTIGATION COMPLETE ===")
    print(f"Evidence file: {evidence_path}")
    print(f"If the color test shows pure black, the issue is in document generation.")
    print(f"If not, the issue is in color configuration or resolution.")
