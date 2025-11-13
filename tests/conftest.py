"""Pytest configuration and shared fixtures."""

import pytest
import pandas as pd
from pathlib import Path
import tempfile
import shutil


@pytest.fixture
def temp_dir():
    """Create temporary directory for test files."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    # Cleanup
    if temp_path.exists():
        shutil.rmtree(temp_path)


@pytest.fixture
def sample_dataframe():
    """Create sample DataFrame for testing."""
    return pd.DataFrame({
        'Column A': [1, 2, 3, 4, 5],
        'Column B': [10.5, 20.3, 30.1, 40.7, 50.2],
        'Column C': ['A', 'B', 'C', 'D', 'E']
    })


@pytest.fixture
def large_dataframe():
    """Create large DataFrame for testing pagination."""
    import numpy as np
    return pd.DataFrame(
        np.random.rand(100, 10),
        columns=[f'Col_{i}' for i in range(10)]
    )


@pytest.fixture
def empty_dataframe():
    """Create empty DataFrame for testing edge cases."""
    return pd.DataFrame()


@pytest.fixture
def sample_image_path(temp_dir):
    """Create a dummy image file for testing."""
    import matplotlib.pyplot as plt
    
    # Create simple test image
    fig, ax = plt.subplots()
    ax.plot([1, 2, 3], [1, 2, 3])
    
    img_path = temp_dir / "test_image.png"
    fig.savefig(img_path)
    plt.close(fig)
    
    return img_path


@pytest.fixture
def sample_qmd_content():
    """Sample Quarto markdown content."""
    return """---
title: "Test Document"
format: html
---

# Introduction

This is a test document.

## Data

```{python}
import pandas as pd
df = pd.DataFrame({'A': [1, 2, 3]})
```
"""


@pytest.fixture
def sample_qmd_file(temp_dir, sample_qmd_content):
    """Create sample Quarto file."""
    qmd_path = temp_dir / "test.qmd"
    qmd_path.write_text(sample_qmd_content, encoding='utf-8')
    return qmd_path


@pytest.fixture
def sample_csv_file(temp_dir, sample_dataframe):
    """Create sample CSV file."""
    csv_path = temp_dir / "test_data.csv"
    sample_dataframe.to_csv(csv_path, index=False)
    return csv_path


@pytest.fixture
def temp_writer(temp_dir):
    """Create temporary DocumentWriter instance for testing."""
    from ePy_docs.writers import DocumentWriter
    
    # Create writer with document_type and layout
    writer = DocumentWriter(document_type='report', layout_style='classic')
    
    yield writer
    
    # Cleanup is automatic via temp_dir fixture


@pytest.fixture
def resolved_layout():
    """Load layout with all references resolved (palette_ref, font_family_ref, etc.)."""
    from ePy_docs.core._config import get_layout_config, get_config_section
    
    def _resolve(layout_name: str = 'classic'):
        """Load layout and resolve all references."""
        layout = get_layout_config(layout_name)
        
        # Resolve palette_ref -> colors
        if 'palette_ref' in layout:
            colors_config = get_config_section('colors')
            palette_name = layout['palette_ref']
            if 'palettes' in colors_config and palette_name in colors_config['palettes']:
                palette = colors_config['palettes'][palette_name]
                layout['colors'] = {'layout_config': {'default_palette': palette_name}, 'palette': palette}
        
        # Resolve font_family_ref -> font_family
        if 'font_family_ref' in layout:
            text_config = get_config_section('text')
            font_ref = layout['font_family_ref']
            if 'font_families' in text_config and font_ref in text_config['font_families']:
                layout['font_family'] = font_ref
                layout['text'] = text_config['font_families'][font_ref]
        
        return layout
    
    return _resolve
