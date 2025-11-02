"""
Code chunk formatting for ePy_docs.

Provides functionality to format code chunks for documentation,
including display-only and executable code blocks.
"""
from typing import Optional


def get_code_config() -> dict:
    """Load code configuration from unified config system."""
    from ePy_docs.core._config import get_config_section
    return get_config_section('code')


def get_available_languages() -> list:
    """Get available programming languages from code configuration."""
    try:
        config = get_code_config()
        return (config.get('programming_languages', {}).keys() or
                config.get('languages', {}).keys() or
                config.get('validation', {}).get('allowed_languages', []))
    except:
        return []


def _format_code_chunk(code: str, language: Optional[str], chunk_type: str, config: dict) -> str:
    """Format a code chunk based on its type."""
    chunk_config = config['formatting'][f'{chunk_type}_chunk']
    validation_config = config['validation']

    if not code:
        raise ValueError("Code content is required.")

    if language is None:
        language = chunk_config['default_language']

    if language not in validation_config['allowed_languages']:
        raise ValueError(f"Language '{language}' not in allowed list: {validation_config['allowed_languages']}")

    formatted_code_block = chunk_config['code_block_format'].format(
        language=language, code=code.strip())

    return (chunk_config['spacing']['before'] + 
            formatted_code_block + 
            chunk_config['spacing']['after'])


def format_code_chunk(code: str, language: Optional[str], chunk_type: str, caption: Optional[str] = None) -> str:
    """Format a code chunk for documentation."""
    config = get_code_config()
    chunk_content = _format_code_chunk(code, language, chunk_type, config)
    
    if caption:
        chunk_config = config['formatting'][f'{chunk_type}_chunk']
        chunk_content += "\n" + chunk_config['caption_format'].format(caption=caption)

    return chunk_content


def format_display_chunk(code: str, language: Optional[str] = None, caption: Optional[str] = None) -> str:
    """Format a display-only code chunk for documentation."""
    return format_code_chunk(code, language, 'display', caption)


def format_executable_chunk(code: str, language: Optional[str] = None, caption: Optional[str] = None) -> str:
    """Format an executable code chunk for documentation."""
    return format_code_chunk(code, language, 'executable', caption)