"""Data utilities for ePy_docs.

This module provides data processing functions for handling Quarto and Markdown files.
"""

from typing import Tuple
from pathlib import Path

__all__ = [
    'process_file', 'process_quarto_file', 'process_markdown_file'
]

def process_file(
    file_path: str,
    file_type: str = None,
    include_yaml: bool = False,
    fix_image_paths: bool = True,
    output_dir: str = None,
    figure_counter: int = 0,
    document_type: str = "report"
) -> Tuple[str, int]:
    """Process a file (Quarto .qmd or Markdown .md) and return its content.
    
    Args:
        file_path: Path to the file
        file_type: Type of file ('quarto', 'markdown', or None to auto-detect)
        include_yaml: Whether to include YAML frontmatter (for Quarto files)
        fix_image_paths: Whether to fix image paths
        output_dir: Output directory for images
        figure_counter: Current figure counter
        document_type: Type of document
        
    Returns:
        Tuple of (content string, updated figure counter)
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Auto-detect file type if not specified
    if file_type is None:
        if path.suffix.lower() == '.qmd':
            file_type = 'quarto'
        elif path.suffix.lower() == '.md':
            file_type = 'markdown'
        else:
            raise ValueError(f"Unsupported file type: {path.suffix}")
    
    content = path.read_text(encoding='utf-8')
    
    # Handle Quarto-specific processing
    if file_type == 'quarto' and not include_yaml and content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            content = parts[2].strip()
    
    return content, figure_counter


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
    return process_file(
        file_path=file_path,
        file_type='quarto',
        include_yaml=include_yaml,
        fix_image_paths=fix_image_paths,
        output_dir=output_dir,
        figure_counter=figure_counter,
        document_type=document_type
    )


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
    return process_file(
        file_path=file_path,
        file_type='markdown',
        fix_image_paths=fix_image_paths,
        output_dir=output_dir,
        figure_counter=figure_counter
    )