"""
Code chunk formatting for ePy_docs.

This module provides functionality to format code chunks for documentation,
including display-only and executable code blocks.
All parameters are sourced from code.json configuration.
"""

import os
import json
from typing import Optional


def _load_code_config() -> dict:
    """Load code configuration from code.json using unified configuration system.
    
    Returns:
        Configuration dictionary from code.json
        
    Raises:
        RuntimeError: If configuration loading fails
        KeyError: If required configuration is missing
    """
    from ePy_docs.core.content import _load_cached_config
    
    try:
        config = _load_cached_config('code')
    except Exception as e:
        raise RuntimeError(f"Failed to load code configuration: {e}")
    
    # Validate required configuration exists
    required_keys = ['formatting', 'validation']
    for key in required_keys:
        if key not in config:
            raise KeyError(f"Required configuration key '{key}' missing in code.json")
    
    return config


def format_display_chunk(code: str, language: str = None, 
                        caption: Optional[str] = None, label: Optional[str] = None) -> str:
    """Format a display-only code chunk (not executable).
    
    Args:
        code: Code content as multiline string
        language: Programming language (if None, uses default from config)
        caption: Optional caption for the code block
        label: Optional label for cross-referencing
        
    Returns:
        Formatted markdown code block
        
    Raises:
        FileNotFoundError: If configuration file is missing
        KeyError: If required configuration is missing
        ValueError: If language is not in allowed list
    """
    config = _load_code_config()
    display_config = config['formatting']['display_chunk']
    validation_config = config['validation']
    
    # Use language from parameter or default from config
    if language is None:
        language = display_config['default_language']
    
    # Validate language is allowed
    if language not in validation_config['allowed_languages']:
        raise ValueError(f"Language '{language}' not in allowed languages: {validation_config['allowed_languages']}")
    
    # Validate required fields
    if not code:
        raise ValueError("Code content is required")
    
    # Build code block using format from config
    chunk_content = display_config['spacing']['before']
    chunk_content += display_config['code_block_format'].format(
        language=language,
        code=code.strip()
    )
    
    # Add caption if provided
    if caption:
        chunk_content += "\n" + display_config['caption_format'].format(caption=caption)
    
    chunk_content += display_config['spacing']['after']
    return chunk_content


def format_executable_chunk(code: str, language: str = None, 
                           caption: Optional[str] = None, label: Optional[str] = None) -> str:
    """Format an executable code chunk (will be executed by Quarto).
    
    Args:
        code: Code content as multiline string
        language: Programming language (if None, uses default from config)
        caption: Optional caption for the code block
        label: Optional label for cross-referencing
        
    Returns:
        Formatted executable code block
        
    Raises:
        FileNotFoundError: If configuration file is missing
        KeyError: If required configuration is missing
        ValueError: If language is not in allowed list
    """
    config = _load_code_config()
    exec_config = config['formatting']['executable_chunk']
    validation_config = config['validation']
    
    # Use language from parameter or default from config
    if language is None:
        language = exec_config['default_language']
    
    # Validate language is allowed
    if language not in validation_config['allowed_languages']:
        raise ValueError(f"Language '{language}' not in allowed languages: {validation_config['allowed_languages']}")
    
    # Validate required fields
    if not code:
        raise ValueError("Code content is required")
    
    # Build code block using format from config
    chunk_content = exec_config['spacing']['before']
    chunk_content += exec_config['code_block_format'].format(
        language=language,
        code=code.strip()
    )
    
    # Add caption if provided
    if caption:
        chunk_content += "\n" + exec_config['caption_format'].format(caption=caption)
    
    chunk_content += exec_config['spacing']['after']
    return chunk_content