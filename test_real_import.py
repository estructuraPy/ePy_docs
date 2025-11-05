"""
Test real-world import scenario with actual user file
"""
import sys
sys.path.append('src')

from ePy_docs import DocumentWriter

# Recreate user's notebook scenario
writer = DocumentWriter('report', layout_style='minimal')

# Add some initial content
writer.add_h1("Test Document with Imported Content")
writer.add_text("This document imports content from external files.")

# Try to import the user's qmd file
try:
    writer.add_quarto_file(r"data\user\document\00_preliminary\front_page.qmd")
    print("✅ Successfully imported front_page.qmd")
    
    # Check content
    content = writer._core.get_content()
    print(f"\nContent length: {len(content)} characters")
    print(f"Buffer items: {len(writer._core.content_buffer)}")
    
except FileNotFoundError:
    print("⚠️ File not found (expected if file doesn't exist)")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
