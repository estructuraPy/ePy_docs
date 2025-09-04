"""Test 002: Creative layout PDF generation with black background.

Generate a PDF document using creative layout to verify
if the black background is correctly applied in the final output.
"""
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ePy_docs.api.quick_setup import setup_report_api
from ePy_docs.api.report import ReportWriter


def test_creative_pdf_generation():
    """Generate PDF with creative layout to test background color."""
    
    # Setup with creative layout
    setup_data = setup_report_api(
        layout='creative',
        project_name="Test Creative Background",
        author="Test System",
        base_path=Path(__file__).parent
    )
    
    # Create writer
    writer = ReportWriter(setup_data)
    
    # Add some content to make background visible
    writer.add_title("TEST: Creative Layout Background")
    writer.add_text("This document tests the creative layout background color.")
    writer.add_text("The background should be black [0, 0, 0] but may appear white.")
    
    # Add a large text block to make background more visible
    writer.add_text("""
    Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod 
    tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, 
    quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.
    
    Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore 
    eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, 
    sunt in culpa qui officia deserunt mollit anim id est laborum.
    """)
    
    # Generate PDF
    output_path = Path(__file__).parent / "evidence_test_002_creative_background.pdf"
    
    try:
        writer.generate_pdf(str(output_path))
        print(f"PDF generated: {output_path}")
        print("Check the PDF background color manually")
        return True
    except Exception as e:
        print(f"Error generating PDF: {e}")
        return False


if __name__ == "__main__":
    result = test_creative_pdf_generation()
    print(f"\nTest result: {'PASS' if result else 'FAIL'}")
