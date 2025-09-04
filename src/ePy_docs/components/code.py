"""
Code chunk formatting for ePy_docs.

This module provides functionality to format code chunks for documentation,
including display-only and executable code blocks, with all parameters
sourced from a JSON configuration.
"""
import os
import json
from typing import Optional

def _load_code_config() -> dict:
    """Load and validate code configuration from a JSON file.

    This function attempts to load the code configuration from a file specified
    in a unified configuration system, ensuring it contains all necessary keys.
    The configuration is cached for subsequent calls.

    Returns:
        The configuration dictionary from the 'code' section of the loaded JSON.

    Raises:
        RuntimeError: If the configuration file fails to load.
        KeyError: If a required configuration key is missing from the file.
    """
    from ePy_docs.components.setup import _load_cached_files, _resolve_config_path

    try:
        config_path = _resolve_config_path('components/code', sync_files=False)
        config = _load_cached_files(config_path, sync_files=False)
    except Exception as e:
        raise RuntimeError(f"Failed to load code configuration: {e}") from e

    required_keys = ['formatting', 'validation']
    for key in required_keys:
        if key not in config:
            raise KeyError(f"Required configuration key '{key}' is missing in code.json")

    return config

def get_available_languages(sync_files: bool = False) -> list:
    """Get available programming languages from code configuration.
    
    Args:
        sync_files: Whether to reload configuration from disk
        
    Returns:
        List of available programming languages
    """
    try:
        from ePy_docs.components.setup import _load_cached_files, _resolve_config_path
        config_path = _resolve_config_path('components/code', sync_files)
        config = _load_cached_files(config_path, sync_files)
        return list(config.get('languages', {}).keys())
    except:
        return []

def _format_code_chunk(code: str, language: Optional[str], chunk_type: str) -> str:
    """Helper function to format a code chunk based on its type.

    Args:
        code: The code content as a multiline string.
        language: The programming language of the code. If None, the default
                  from the configuration is used.
        chunk_type: The type of chunk to format, either 'display' or 'executable'.

    Returns:
        The formatted markdown code block string.

    Raises:
        ValueError: If the code content is empty or the language is not in the
                    list of allowed languages.
        KeyError: If a required key is missing in the configuration.
    """
    config = _load_code_config()
    chunk_config = config['formatting'].get(f'{chunk_type}_chunk')
    if not chunk_config:
        raise KeyError(f"Configuration for chunk type '{chunk_type}' not found.")
    validation_config = config['validation']

    if not code:
        raise ValueError("Code content is required.")

    if language is None:
        language = chunk_config['default_language']

    if language not in validation_config['allowed_languages']:
        raise ValueError(f"Language '{language}' is not in the allowed list: {validation_config['allowed_languages']}")

    formatted_code_block = chunk_config['code_block_format'].format(
        language=language,
        code=code.strip()
    )

    return (
        chunk_config['spacing']['before'] +
        formatted_code_block +
        chunk_config['spacing']['after']
    )

def format_display_chunk(code: str, language: Optional[str] = None,
                         caption: Optional[str] = None, label: Optional[str] = None) -> str:
    """Format a display-only code chunk for documentation.

    This function formats a block of code to be displayed in documentation without
    being executed. The formatting follows the configuration defined in
    'code.json' under the 'display_chunk' section.

    Args:
        code: The code content as a multiline string.
        language: The programming language. If None, the default language from
                  the configuration is used.
        caption: An optional caption for the code block.
        label: An optional label for cross-referencing.

    Returns:
        The formatted markdown code block as a string.

    Raises:
        RuntimeError: If the configuration fails to load.
        KeyError: If a required configuration key is missing.
        ValueError: If the provided language is not allowed or the code is empty.

    Assumptions:
        - The `_load_code_config` function is correctly implemented and returns
          a valid dictionary.
        - The `code.json` file contains 'formatting' and 'validation' keys
          with the necessary sub-keys.
    """
    chunk_content = _format_code_chunk(code, language, 'display')
    config = _load_code_config()
    display_config = config['formatting']['display_chunk']

    if caption:
        chunk_content += "\n" + display_config['caption_format'].format(caption=caption)
    
    return chunk_content

def format_executable_chunk(code: str, language: Optional[str] = None,
                            caption: Optional[str] = None, label: Optional[str] = None) -> str:
    """Format an executable code chunk for documentation.

    This function formats a code block intended for execution within the documentation
    framework (e.g., by Quarto). The formatting is controlled by the
    'executable_chunk' section of 'code.json'.

    Args:
        code: The code content as a multiline string.
        language: The programming language. If None, the default language from
                  the configuration is used.
        caption: An optional caption for the code block.
        label: An optional label for cross-referencing.

    Returns:
        The formatted executable code block as a string.

    Raises:
        RuntimeError: If the configuration fails to load.
        KeyError: If a required configuration key is missing.
        ValueError: If the provided language is not allowed or the code is empty.

    Assumptions:
        - The `_load_code_config` function is correctly implemented and returns
          a valid dictionary.
        - The `code.json` file contains 'formatting' and 'validation' keys
          with the necessary sub-keys.
    """
    chunk_content = _format_code_chunk(code, language, 'executable')
    config = _load_code_config()
    exec_config = config['formatting']['executable_chunk']

    if caption:
        chunk_content += "\n" + exec_config['caption_format'].format(caption=caption)

    return chunk_content