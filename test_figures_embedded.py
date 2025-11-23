"""
Verify that figures configuration still works after removing figures.epyson
"""

import sys
from pathlib import Path

# Clear cache
for module in list(sys.modules.keys()):
    if 'ePy_docs' in module:
        del sys.modules[module]

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from ePy_docs.core._config import load_layout, clear_global_cache
clear_global_cache()

print("=" * 70)
print("TEST: Figures Configuration (Post figures.epyson Deletion)")
print("=" * 70)

test_layouts = ['academic', 'classic', 'corporate', 'creative', 'handwritten',
                'minimal', 'professional', 'scientific', 'technical']

print("\n[Test] Checking figures configuration in all layouts...\n")

all_good = True
for layout_name in test_layouts:
    try:
        layout = load_layout(layout_name, resolve_refs=True)
        
        # Check if figures exists
        if 'figures' not in layout:
            print(f"✗ {layout_name:15} - Missing 'figures' configuration")
            all_good = False
            continue
        
        figures = layout['figures']
        
        # Check essential keys
        has_caption = 'caption' in figures
        has_numbering = figures.get('caption', {}).get('numbering') is not None
        has_format = 'format' in figures.get('caption', {})
        
        if has_caption and has_numbering and has_format:
            numbering = figures['caption']['numbering']
            caption_format = figures['caption']['format']
            print(f"✓ {layout_name:15} - numbering: {numbering}, format: {caption_format}")
        else:
            print(f"⚠ {layout_name:15} - Incomplete caption configuration")
            all_good = False
            
    except Exception as e:
        print(f"✗ {layout_name:15} - Error: {e}")
        all_good = False

print("\n" + "=" * 70)
if all_good:
    print("✓ ALL TESTS PASSED - figures.epyson successfully eliminated")
    print("  All layouts have embedded figures configuration")
else:
    print("✗ SOME TESTS FAILED - Check output above")
print("=" * 70)
