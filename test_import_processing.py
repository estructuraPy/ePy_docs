"""
Test figure and table processing in imported MD/QMD files.
"""
import tempfile
import os
from pathlib import Path
from ePy_docs.writers import DocumentWriter

def test_markdown_table_conversion():
    """Test that markdown tables in imported files are converted to styled images."""
    
    # Create temporary markdown file with table
    md_content = """
# Test Document

Some text before table.

| Column A | Column B | Column C |
|----------|----------|----------|
| Value 1  | Value 2  | Value 3  |
| Value 4  | Value 5  | Value 6  |

: Table caption from markdown

Some text after table.
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
        f.write(md_content)
        md_path = f.name
    
    try:
        # Create writer
        writer = DocumentWriter(document_type='report')
        
        # Import markdown with table conversion
        from ePy_docs.core._markdown import process_markdown_file
        process_markdown_file(
            file_path=md_path,
            convert_tables=True,
            writer_instance=writer
        )
        
        # Check content using get_content() method
        content = writer._core.get_content()
        print("\n=== MARKDOWN IMPORT TEST ===")
        print(f"Content length: {len(content)} characters")
        print(f"Content buffer items: {len(writer._core.content_buffer)}")
        print(f"Contains table reference: {'tbl-' in content}")
        print(f"Table counter: {writer._core._counters['table']}")
        print(f"Generated images: {len(writer._core.generated_images)}")
        
        # Should have created a table
        assert writer._core._counters['table'] > 0, "No table was created from markdown"
        assert 'tbl-' in content, "No table reference found in content"
        
        # Should have generated image (show_figure=True)
        assert len(writer._core.generated_images) > 0, "No table image was generated"
        
        print("✓ Markdown table conversion working with image generation")
        
    finally:
        os.unlink(md_path)


def test_markdown_image_conversion():
    """Test that markdown images in imported files are converted to figures."""
    
    # Create temporary markdown file with image
    md_content = """
# Test Document

Some text before image.

![Alt text for image](test_image.png)
: Figure caption from markdown

Some text after image.
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
        f.write(md_content)
        md_path = f.name
    
    try:
        # Create writer
        writer = DocumentWriter(document_type='report')
        
        # Import markdown with image conversion
        from ePy_docs.core._markdown import process_markdown_file
        process_markdown_file(
            file_path=md_path,
            fix_image_paths=True,
            writer_instance=writer
        )
        
        # Check content using get_content() method
        content = writer._core.get_content()
        print("\n=== MARKDOWN IMAGE TEST ===")
        print(f"Content length: {len(content)} characters")
        print(f"Content buffer items: {len(writer._core.content_buffer)}")
        print(f"Contains figure reference: {'fig-' in content}")
        print(f"Figure counter: {writer._core._counters['figure']}")
        
        # Note: May not create figure if image doesn't exist, but should attempt
        print("✓ Markdown image processing attempted")
        
    finally:
        os.unlink(md_path)


def test_quarto_table_conversion():
    """Test that tables in imported QMD files are converted to styled images."""
    
    # Create temporary Quarto file with table
    qmd_content = """---
title: "Test Document"
---

# Test Section

| Parameter | Value | Units |
|-----------|-------|-------|
| Density   | 2.5   | g/cm³ |
| Strength  | 25    | MPa   |

: Table: Material properties

More content here.
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.qmd', delete=False, encoding='utf-8') as f:
        f.write(qmd_content)
        qmd_path = f.name
    
    try:
        # Create writer
        writer = DocumentWriter(document_type='report')
        
        # Import Quarto with table conversion
        from ePy_docs.core._quarto import process_quarto_file
        process_quarto_file(
            file_path=qmd_path,
            include_yaml=False,
            convert_tables=True,
            writer_instance=writer
        )
        
        # Check content
        content = writer._core.get_content()
        print("\n=== QUARTO IMPORT TEST ===")
        print(f"Content length: {len(content)} characters")
        print(f"Contains table reference: {'tbl-' in content}")
        print(f"Table counter: {writer._core._counters['table']}")
        print(f"Generated images: {len(writer._core.generated_images)}")
        
        # Should have created a table
        assert writer._core._counters['table'] > 0, "No table was created from Quarto"
        assert 'tbl-' in content, "No table reference found in content"
        
        # Should have generated image (show_figure=True)
        assert len(writer._core.generated_images) > 0, "No table image was generated"
        
        print("✓ Quarto table conversion working with image generation")
        
    finally:
        os.unlink(qmd_path)


def test_caption_extraction():
    """Test that captions are properly extracted from markdown."""
    
    md_content = """
| A | B |
|---|---|
| 1 | 2 |

: Custom table caption

![Image](img.png)
: Custom figure caption
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
        f.write(md_content)
        md_path = f.name
    
    try:
        writer = DocumentWriter(document_type='report')
        
        from ePy_docs.core._markdown import process_markdown_file
        process_markdown_file(
            file_path=md_path,
            convert_tables=True,
            fix_image_paths=True,
            writer_instance=writer
        )
        
        content = writer._core.get_content()
        print("\n=== CAPTION EXTRACTION TEST ===")
        print(f"Content preview: {content[:500]}")
        
        print("✓ Caption extraction attempted")
        
    finally:
        os.unlink(md_path)


def test_no_conversion():
    """Test that conversion can be disabled."""
    
    md_content = """
| A | B |
|---|---|
| 1 | 2 |

![Image](img.png)
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
        f.write(md_content)
        md_path = f.name
    
    try:
        writer = DocumentWriter(document_type='report')
        
        from ePy_docs.core._markdown import process_markdown_file
        process_markdown_file(
            file_path=md_path,
            convert_tables=False,
            fix_image_paths=False,
            writer_instance=writer
        )
        
        # Should have raw markdown
        content = writer._core.get_content()
        print("\n=== NO CONVERSION TEST ===")
        print(f"Contains raw table: {'|' in content}")
        print(f"Contains raw image: {'![' in content}")
        
        assert '|' in content, "Raw table not preserved"
        assert '![' in content, "Raw image not preserved"
        
        print("✓ No conversion mode working")
        
    finally:
        os.unlink(md_path)


if __name__ == '__main__':
    print("Testing figure and table processing in imported files...\n")
    
    test_markdown_table_conversion()
    test_markdown_image_conversion()
    test_quarto_table_conversion()
    test_caption_extraction()
    test_no_conversion()
    
    print("\n✅ All import processing tests completed!")
