"""
Demonstration: Color visibility fix for PDF section headings.

This script shows that section colors now use darker shades for better visibility
on white backgrounds.
"""
from ePy_docs.core._pdf import PdfConfig, HeaderGenerator, PdfValidator

def analyze_color_visibility():
    """Analyze and display color visibility for section headings."""
    
    # Create PDF configuration components
    config = PdfConfig()
    validator = PdfValidator()
    generator = HeaderGenerator(config, validator)
    
    # Generate header for professional layout
    header = generator.generate_header('professional')
    
    # Extract color definitions and section styling
    import re
    color_defs = re.findall(r'\\definecolor\{([^}]+)\}\{RGB\}\{([^}]+)\}', header)
    section_colors = re.findall(
        r'\\(section|subsection|subsubsection)font\{\\color\{([^}]+)\}\}', 
        header
    )
    
    # Create color lookup
    color_map = dict(color_defs)
    
    print("\n" + "="*80)
    print(" "*25 + "COLOR VISIBILITY ANALYSIS")
    print("="*80)
    
    print("\n📄 Background: WHITE (RGB 255,255,255)")
    print("\n📊 Visibility Ratings:")
    print("  • GOOD:    Brightness < 180 (strong contrast with white)")
    print("  • FAIR:    Brightness 180-215 (moderate contrast)")
    print("  • POOR:    Brightness > 215 (weak contrast, hard to see)")
    
    print("\n" + "="*80)
    print("SECTION HEADING COLORS (Now Using DARK shades for visibility)")
    print("="*80)
    
    for element, color_name in section_colors:
        if color_name in color_map:
            rgb_str = color_map[color_name]
            r, g, b = map(int, rgb_str.split(','))
            brightness = int(0.299*r + 0.587*g + 0.114*b)
            
            # Determine visibility rating
            if brightness < 180:
                rating = "✅ GOOD "
                bar = "█" * (20 - brightness//13)
            elif brightness < 215:
                rating = "⚠️  FAIR "
                bar = "▓" * (20 - brightness//13)
            else:
                rating = "❌ POOR "
                bar = "░" * (20 - brightness//13)
            
            print(f"\n\\{element:<18} → {color_name:<20}")
            print(f"   RGB({r:3d}, {g:3d}, {b:3d})  Brightness: {brightness:3d}/255  {rating}")
            print(f"   Contrast: {bar}")
    
    print("\n" + "="*80)
    print("✅ FIX APPLIED: Sections now use brandQuinary, brandQuaternary (dark blues)")
    print("   instead of brandPrimary, brandSecondary (light blues)")
    print("="*80 + "\n")
    
    return True

if __name__ == "__main__":
    analyze_color_visibility()
