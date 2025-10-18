"""Data utilities for ePy_docs.

This module provides data processing functions for handling Quarto and Markdown files.
"""

from typing import Tuple
from pathlib import Path

__all__ = [
    'process_quarto_file', 'process_markdown_file'
]

def process_quarto_file(
    file_path: str,
    include_yaml: bool = False,
    fix_image_paths: bool = True,
    output_dir: str = None,
    figure_counter: int = 0,
    document_type: str = "report"
) -> Tuple[str, int]:
    """Process a Quarto (.qmd) file and return its content.
    
    Args:
        file_path: Path to the .qmd file
        include_yaml: Whether to include YAML frontmatter
        fix_image_paths: Whether to fix image paths
        output_dir: Output directory for images
        figure_counter: Current figure counter
        document_type: Type of document
        
    Returns:
        Tuple of (content string, updated figure counter)
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Quarto file not found: {file_path}")
    
    content = path.read_text(encoding='utf-8')
    
    # Remove YAML frontmatter if requested
    if not include_yaml and content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            content = parts[2].strip()
    
    return content, figure_counter


def process_markdown_file(
    file_path: str,
    fix_image_paths: bool = True,
    output_dir: str = None,
    figure_counter: int = 0
) -> Tuple[str, int]:
    """Process a Markdown (.md) file and return its content.
    
    Args:
        file_path: Path to the .md file
        fix_image_paths: Whether to fix image paths
        output_dir: Output directory for images
        figure_counter: Current figure counter
        
    Returns:
        Tuple of (content string, updated figure counter)
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Markdown file not found: {file_path}")
    
    content = path.read_text(encoding='utf-8')
    return content, figure_counter