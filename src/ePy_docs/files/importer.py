"""
File import utilities for ePy_docs FILES world.

Pure file I/O operations for importing external content files.
TERRITORIAL SCOPE: FILES world (reading) - COMPONENTS world handles processing.
"""

import os
from typing import Tuple

def remove_yaml_frontmatter(content: str) -> str:
    """Remove YAML frontmatter from content.
    
    Args:
        content: File content that may contain YAML frontmatter
        
    Returns:
        Content with YAML frontmatter removed
    """
    lines = content.split('\n')
    if lines and lines[0].strip() == '---':
        # Find the closing ---
        end_yaml = None
        for i, line in enumerate(lines[1:], 1):
            if line.strip() == '---':
                end_yaml = i
                break
        
        if end_yaml is not None:
            # Remove YAML section
            return '\n'.join(lines[end_yaml + 1:])
    
    return content

def process_quarto_file(file_path: str, include_yaml: bool = False, 
                       fix_image_paths: bool = True, output_dir: str = None,
                       figure_counter: int = 0) -> Tuple[str, int]:
    """Process a Quarto (.qmd) file for import.
    
    Pure file reading operation with basic YAML processing.
    Image path fixing delegated to COMPONENTS world when needed.
    
    Args:
        file_path: Path to the .qmd file to import
        include_yaml: Whether to include YAML frontmatter (default: False)
        fix_image_paths: Whether to automatically fix image paths (default: True)
        output_dir: Target output directory (required if fix_image_paths=True)
        figure_counter: Current figure counter (for path fixing)
        
    Returns:
        Tuple of (processed_content, updated_figure_counter)
        
    Raises:
        FileNotFoundError: If the file doesn't exist
    """
    # Pure file I/O - no wrapper contamination
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Quarto file not found: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if not include_yaml:
        content = remove_yaml_frontmatter(content)
    
    # Delegate image processing to COMPONENTS world (territorial boundary)
    if fix_image_paths and output_dir:
        from ePy_docs.components.markdown import MarkdownFormatter
        content, figure_counter = MarkdownFormatter.fix_image_paths_in_imported_content(
            content, file_path, output_dir, figure_counter
        )
    
    return content, figure_counter

def process_markdown_file(file_path: str, fix_image_paths: bool = True, 
                         output_dir: str = None, figure_counter: int = 0) -> Tuple[str, int]:
    """Process a Markdown (.md) file for import.
    
    Pure file reading operation.
    Image path fixing delegated to COMPONENTS world when needed.
    
    Args:
        file_path: Path to the .md file to import
        fix_image_paths: Whether to automatically fix image paths (default: True)
        output_dir: Target output directory (required if fix_image_paths=True)
        figure_counter: Current figure counter (for path fixing)
        
    Returns:
        Tuple of (processed_content, updated_figure_counter)
        
    Raises:
        FileNotFoundError: If the file doesn't exist
    """
    # Pure file I/O - no wrapper contamination
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Markdown file not found: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Delegate image processing to COMPONENTS world (territorial boundary)
    if fix_image_paths and output_dir:
        from ePy_docs.components.markdown import MarkdownFormatter
        content, figure_counter = MarkdownFormatter.fix_image_paths_in_imported_content(
            content, file_path, output_dir, figure_counter
        )
    
    return content, figure_counter

def format_imported_content(content: str) -> str:
    """Format imported content with proper spacing.
    
    Args:
        content: Content to format
        
    Returns:
        Formatted content with proper spacing
    """
    return f"\n{content.strip()}\n\n"
