"""Test font configuration for brand font (Helvetica)."""

from src.ePy_docs.core._config import get_font_latex_config

# Test brand font configuration
print("=" * 60)
print("Testing brand font configuration (corporate layout)")
print("=" * 60)

latex_config = get_font_latex_config(layout_name='corporate')
print(latex_config)

print("\n" + "=" * 60)
print("Expected to see:")
print("- Path pointing to: d:/Dropbox/Family Room/...")
print("- Font: helvetica_lt_std_compressed.otf")
print("=" * 60)
