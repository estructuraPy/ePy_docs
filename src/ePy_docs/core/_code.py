"""
Code chunk formatting for ePy_docs.

Provides functionality to format code chunks for documentation,
including display-only and executable code blocks.

Design: Configuration-driven architecture - loads all formatting rules from code.epyson.
Follows Single Responsibility Principle - only handles code formatting.
"""
from typing import Optional, Dict, Any


# Configuration cache (lazy loading)
_config_cache: Optional[Dict[str, Any]] = None


def _load_code_config() -> Dict[str, Any]:
    """Load code configuration from code.epyson with caching.
    
    Returns:
        Complete code configuration dictionary
        
    Raises:
        RuntimeError: If configuration cannot be loaded
    """
    global _config_cache
    
    if _config_cache is not None:
        return _config_cache
    
    try:
        from ePy_docs.core._config import get_config_section
        
        config = get_config_section('code')
        
        # Validate required sections exist - simplified structure
        if 'display_chunk' not in config:
            raise ValueError("Missing 'display_chunk' section in code configuration")
        if 'executable_chunk' not in config:
            raise ValueError("Missing 'executable_chunk' section in code configuration")
        
        _config_cache = config
        return config
        
    except (ImportError, KeyError, ValueError) as e:
        raise RuntimeError(f"Code configuration not available: {e}")


def get_available_languages() -> list:
    """Get available programming languages for code chunks.
    
    Returns:
        List of supported language identifiers for syntax highlighting.
        
    Example:
        languages = get_available_languages()
        print(f"Supported: {', '.join(languages)}")
    """
    config = _load_code_config()
    return config['validation']['allowed_languages'].copy()


def _validate_inputs(code: str, language: Optional[str], chunk_type: str, config: Optional[Dict[str, Any]] = None) -> str:
    """Validate and normalize inputs for code chunk formatting.
    
    Args:
        code: Source code content to validate
        language: Programming language identifier
        chunk_type: Type of chunk ('display' or 'executable')
        
    Returns:
        Normalized language identifier
        
    Raises:
        ValueError: If code is None, empty, or language is invalid
    """
    if code is None or not code or not code.strip():
        raise ValueError("Code content is required")
    
    # Load configuration
    if config is None:
        config = _load_code_config()
    
    # Get chunk configuration
    chunk_key = f'{chunk_type}_chunk'
    if chunk_key not in config:
        raise ValueError(f"Unknown chunk type: '{chunk_type}'")
    
    chunk_config = config[chunk_key]
    allowed_languages = config.get('allowed_languages', ['python', 'javascript', 'html', 'css', 'sql', 'bash', 'yaml', 'json'])
    
    # Use default language if none specified
    if language is None:
        language = 'python'  # Default fallback
    
    # Validate language
    if language not in allowed_languages:
        raise ValueError(f"Language '{language}' not supported. Available: {', '.join(allowed_languages)}")
    
    return language


def _get_callout_type_for_layout(layout_name: str = "default") -> str:
    """Get appropriate callout type for code chunks based on layout.
    
    Args:
        layout_name: Name of the layout
        
    Returns:
        Callout type that matches the layout's aesthetic
    """
    # Map layouts to callout types that work well for code
    layout_callout_map = {
        'minimal': 'note',
        'scientific': 'note', 
        'technical': 'tip',
        'creative': 'important',
        'professional': 'note',
        'academic': 'note',
        'corporate': 'note',
        'classic': 'note',
        'handwritten': 'tip',
        'default': 'note'
    }
    
    return layout_callout_map.get(layout_name, 'note')


def _format_code_chunk(code: str, language: str, chunk_type: str, config: Optional[Dict[str, Any]] = None) -> str:
    """Format a code chunk with universal styling that works in both HTML and PDF.
    
    Args:
        code: Source code content (already validated)
        language: Programming language identifier (already validated)
        chunk_type: Type of chunk ('display' or 'executable')
        config: Configuration dictionary with layout information
        
    Returns:
        Formatted code block using Quarto callouts for universal compatibility
    """
    if config is None:
        config = _load_code_config()
    
    chunk_key = f'{chunk_type}_chunk'
    if chunk_key not in config:
        raise ValueError(f"Unknown chunk type: '{chunk_type}'")
    
    chunk_config = config[chunk_key]
    
    # Validate required fields
    if 'code_block_format' not in chunk_config:
        raise ValueError(f"Missing 'code_block_format' in {chunk_key} configuration")
    if 'spacing' not in chunk_config:
        raise ValueError(f"Missing 'spacing' in {chunk_key} configuration")
    
    # Format code block
    formatted_code_block = chunk_config['code_block_format'].format(
        language=language, 
        code=code.strip()
    )
    
    # Check if visual formatting is configured
    format_config = config.get('format', {})
    layout_name = config.get('layout_name', 'default')
    
    # Apply visual formatting using callouts for universal compatibility
    if format_config:
        callout_type = _get_callout_type_for_layout(layout_name)
        
        # Wrap in callout with simple appearance and no icon for clean code display
        formatted_code_block = f''':::{{{".callout-" + callout_type} appearance="simple" icon="false" collapse="false"}}

{formatted_code_block}

:::'''
    
    # Add spacing
    spacing = chunk_config['spacing']
    if 'before' not in spacing or 'after' not in spacing:
        raise ValueError(f"Missing 'before' or 'after' in spacing configuration for {chunk_key}")
    
    return (spacing['before'] + formatted_code_block + spacing['after'])


def format_code_chunk(code: str, language: Optional[str], chunk_type: str, caption: Optional[str] = None, config: Optional[Dict[str, Any]] = None, counter: int = 1) -> str:
    """Format a code chunk for documentation.
    
    Args:
        code: Source code content to format
        language: Programming language identifier for syntax highlighting
        chunk_type: Type of chunk ('display' or 'executable')
        caption: Optional caption text
        
    Returns:
        Formatted markdown code block
        
    Raises:
        ValueError: If code is empty or language is invalid
        TypeError: If code is None
    """
    # Load configuration if not provided
    if config is None:
        config = _load_code_config()
    
    # Validate inputs and get normalized language
    validated_language = _validate_inputs(code, language, chunk_type, config)
    
    # Format the chunk
    chunk_content = _format_code_chunk(code, validated_language, chunk_type, config)
    
    # Add caption if provided
    if caption:
        chunk_key = f'{chunk_type}_chunk'
        
        if chunk_key not in config:
            raise ValueError(f"Unknown chunk type: '{chunk_type}'")
        
        chunk_config = config[chunk_key]
        
        if 'caption_format' not in chunk_config:
            raise ValueError(f"Missing 'caption_format' in {chunk_key} configuration")
        
        chunk_content += chunk_config['caption_format'].format(caption=caption, counter=counter)
    
    return chunk_content


def format_display_chunk(code: str, language: Optional[str] = None, caption: Optional[str] = None, config: Optional[Dict[str, Any]] = None, counter: int = 1) -> str:
    """Format a display-only code chunk for documentation.
    
    Creates a standard markdown code block for display purposes only.
    
    Args:
        code: Source code to display
        language: Programming language for syntax highlighting (default: python)
        caption: Optional caption text
        config: Code configuration (uses layout-integrated config if not provided)
        
    Returns:
        Formatted markdown code block
        
    Example:
        chunk = format_display_chunk("print('hello')", language='python')
        # Returns: "\\n\\n```python\\nprint('hello')\\n```\\n\\n"
    """
    return format_code_chunk(code, language, 'display', caption, config, counter)


def format_executable_chunk(code: str, language: Optional[str] = None, caption: Optional[str] = None, config: Optional[Dict[str, Any]] = None, counter: int = 1) -> str:
    """Format an executable code chunk for documentation.
    
    Creates a Quarto-style executable code block with curly braces syntax.
    
    Args:
        code: Source code to execute
        language: Programming language for execution (default: python)
        caption: Optional caption text
        config: Code configuration (uses layout-integrated config if not provided)
        
    Returns:
        Formatted executable code block
        
    Example:
        chunk = format_executable_chunk("x = 42", language='python')
        # Returns: "\\n\\n```{python}\\nx = 42\\n```\\n\\n"
    """
    return format_code_chunk(code, language, 'executable', caption, config, counter)