"""Test the corrected Helvetica font configuration."""

from src.ePy_docs.core._config import get_font_latex_config

print("=" * 70)
print("Testing Helvetica font with correct filename (with spaces)")
print("=" * 70)

# Test brand font configuration with corporate layout
latex_config = get_font_latex_config(layout_name='corporate')

print("\n📝 Generated LaTeX configuration:")
print("-" * 70)
print(latex_config)
print("-" * 70)

# Check for specific elements
checks = [
    ("Font path", "d:/Dropbox/Family Room/A_Gestion/300_GestiónEmpresarial/20_ImagenCorporativa/01_ManualMarca/tipografías_1_0_0/" in latex_config),
    ("Font filename", "helvetica lt_std_compressed" in latex_config),
    ("Extension OTF", "Extension = .OTF" in latex_config or "Extension = .otf" in latex_config),
    ("setmainfont", "setmainfont" in latex_config),
    ("setsansfont", "setsansfont" in latex_config),
]

print("\n✓ Configuration verification:")
for check_name, result in checks:
    status = "✅" if result else "❌"
    print(f"  {status} {check_name}: {result}")

print("\n" + "=" * 70)
print("Expected filename: 'helvetica lt_std_compressed.OTF' (with spaces)")
print("Font name in LaTeX: 'Helvetica LT Std Compressed'")
print("=" * 70)
