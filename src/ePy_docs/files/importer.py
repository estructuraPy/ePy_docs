"""
File import utilities for ePy_docs.

This module provides functions to import and process content from external files
(Quarto .qmd files and Markdown .md files) with path fixing and content processing.
"""

import os
from typing import Tuple

def validate_file_exists(file_path: str, file_type: str) -> None:
    """Validate that a file exists.
    
    Args:
        file_path: Path to the file to check
        file_type: Type of file for error message (e.g., "Quarto", "Markdown")
        
    Raises:
        FileNotFoundError: If the file doesn't exist
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"{file_type} file not found: {file_path}")

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

def fix_image_paths_in_content(content: str, source_file_path: str, 
                              target_output_dir: str, figure_counter: int) -> Tuple[str, int]:
    """Fix image paths in imported content.
    
    Args:
        content: Content with potentially incorrect image paths
        source_file_path: Path to the source file being imported
        target_output_dir: Target output directory for the final document
        figure_counter: Current figure counter
        
    Returns:
        Tuple of (fixed_content, updated_figure_counter)
    """
    from ePy_docs.core.markdown import MarkdownFormatter
    return MarkdownFormatter.fix_image_paths_in_imported_content(
        content, source_file_path, target_output_dir, figure_counter
    )

def read_file_content(file_path: str) -> str:
    """Read content from a file.
    
    Args:
        file_path: Path to the file to read
        
    Returns:
        File content as string
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def process_quarto_file(file_path: str, include_yaml: bool = False, 
                       fix_image_paths: bool = True, output_dir: str = None,
                       figure_counter: int = 0) -> Tuple[str, int]:
    """Process a Quarto (.qmd) file for import.
    
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
    validate_file_exists(file_path, "Quarto")
    
    content = read_file_content(file_path)
    
    if not include_yaml:
        content = remove_yaml_frontmatter(content)
    
    # Fix image paths if requested
    if fix_image_paths and output_dir:
        content, figure_counter = fix_image_paths_in_content(
            content, file_path, output_dir, figure_counter
        )
    
    return content, figure_counter

def process_markdown_file(file_path: str, fix_image_paths: bool = True, 
                         output_dir: str = None, figure_counter: int = 0) -> Tuple[str, int]:
    """Process a Markdown (.md) file for import.
    
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
    validate_file_exists(file_path, "Markdown")
    
    content = read_file_content(file_path)
    
    # Fix image paths if requested
    if fix_image_paths and output_dir:
        content, figure_counter = fix_image_paths_in_content(
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
