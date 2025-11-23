"""
🔄 RESTART HELPER - Run this in your Jupyter notebook

Add this cell at the TOP of your notebook and run it to clear all caches:
"""

# ============================================================================
# CACHE CLEARING CODE - Run this first!
# ============================================================================

import sys

# Clear ALL cached ePy_docs modules
print("🔄 Clearing cached modules...")
cached_modules = [m for m in list(sys.modules.keys()) if 'ePy_docs' in m]
for module in cached_modules:
    del sys.modules[module]
print(f"✓ Cleared {len(cached_modules)} cached modules\n")

# Fresh import
from ePy_docs import DocumentWriter
from ePy_docs.core._config import clear_global_cache

# Clear configuration cache
clear_global_cache()
print("✓ Configuration cache cleared\n")

print("=" * 70)
print("✓ CACHE CLEARED - Ready to use!")
print("=" * 70)
print("\nYou can now use DocumentWriter normally:")
print("  writer = DocumentWriter(document_type='report', layout_style='technical')")
print("  writer.add_text('# My Document')")
print("  writer.generate()")

# ============================================================================
# After running this cell, your notebook is ready to use!
# ============================================================================
