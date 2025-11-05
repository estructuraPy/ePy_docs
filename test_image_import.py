"""
Test importing markdown with actual images
"""
import sys
sys.path.append('src')

from ePy_docs import DocumentWriter
import tempfile
import os
from pathlib import Path
from PIL import Image

# Create a test image
test_img_dir = Path(tempfile.mkdtemp())
test_img_path = test_img_dir / "test_figure.png"

# Create simple test image
img = Image.new('RGB', (100, 100), color='blue')
img.save(test_img_path)

print(f"Created test image: {test_img_path}")

# Create markdown with reference to this image
md_content = f"""
# Document with Image

Some text before the image.

![Test Image]({test_img_path.name})
: Figure caption for imported image

Some text after the image.
"""

md_path = test_img_dir / "test.md"
with open(md_path, 'w', encoding='utf-8') as f:
    f.write(md_content)

try:
    writer = DocumentWriter('report')
    
    # Import markdown with image
    print(f"Importing from: {md_path}")
    print(f"Base dir will be: {md_path.parent}")
    print(f"Expected resolved path: {md_path.parent / test_img_path.name}")
    
    writer.add_markdown_file(str(md_path), fix_image_paths=True)
    
    print(f"\nFigure counter: {writer._core._counters['figure']}")
    print(f"Generated images: {len(writer._core.generated_images)}")
    
    content = writer._core.get_content()
    
    if 'fig-1' in content:
        print("✅ Image imported and numbered correctly!")
        print(f"✅ Image saved with consecutive numbering")
    else:
        print("⚠️ Image reference not found in content")
        print(f"Content preview: {content[:200]}")
    
finally:
    # Cleanup
    os.unlink(test_img_path)
    os.unlink(md_path)
    os.rmdir(test_img_dir)
