"""
Code chunk utilities for ePy_docs.

This module provides functions to create and format code chunks for display
in technical reports, both executable and non-executable.
"""

from typing import Optional


def create_display_chunk(code: str, language: str = 'python', 
                        caption: Optional[str] = None, label: Optional[str] = None) -> str:
    """Create non-executable code chunk for display only.
    
    Args:
        code: Code content as multiline string
        language: Programming language (python, javascript, sql, etc.)
        caption: Optional caption for the code block
        label: Optional label for cross-referencing
        
    Returns:
        Formatted code chunk as string
        
    Example:
        # Display only code block
        chunk = create_display_chunk('''
        Length unit: $mm$
        Area unit: $m^2$
        Force unit: $kN$
        ''', language='text')
        
        # Display Python code without execution
        chunk = create_display_chunk('''
        import numpy as np
        x = np.array([1, 2, 3, 4, 5])
        mean_value = np.mean(x)
        print(f"Mean: {mean_value}")
        ''', language='python', caption='Python code example')
    """
    # Display-only code block (plain markdown format - no execution)
    chunk_content = f"\n```{language}\n{code.strip()}\n```\n"
    
    # Add caption if provided (for display-only, use standard markdown caption)
    if caption:
        chunk_content += f"\n: {caption}\n"
    
    chunk_content += "\n"
    return chunk_content


def create_executable_chunk(code: str, language: str = 'python', 
                           caption: Optional[str] = None, label: Optional[str] = None) -> str:
    """Create executable code chunk for Quarto execution.
    
    Args:
        code: Code content as multiline string
        language: Programming language (python, javascript, r, etc.)
        caption: Optional caption for the code block
        label: Optional label for cross-referencing
        
    Returns:
        Formatted executable code chunk as string
        
    Example:
        # Executable Python code
        chunk = create_executable_chunk('''
        import numpy as np
        x = np.array([1, 2, 3, 4, 5])
        mean_value = np.mean(x)
        print(f"Mean: {mean_value}")
        ''', language='python', caption='Calculate mean of array')
        
        # Executable R code
        chunk = create_executable_chunk('''
        data <- c(1, 2, 3, 4, 5)
        mean_value <- mean(data)
        print(paste("Mean:", mean_value))
        ''', language='r', caption='R calculation example')
    """
    # Executable code block (Quarto will execute this)
    chunk_content = f"\n```{{{language}}}\n{code.strip()}\n```\n"
    
    # Add caption as text after the code block for executable chunks
    if caption:
        chunk_content += f"\n*{caption}*\n"
    
    chunk_content += "\n"
    return chunk_content
