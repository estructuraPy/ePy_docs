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
    """Load base code configuration from code.epyson with caching.
    
    Returns:
        Base code configuration dictionary with chunk_types and validation
        
    Raises:
        RuntimeError: If configuration cannot be loaded
    """
    global _config_cache
    
    if _config_cache is not None:
        return _config_cache
    
    try:
        from ePy_docs.core._config import get_config_section
        
        config = get_config_section('code')
        
        # Validate required sections
        if 'chunk_types' not in config:
            raise ValueError("Missing 'chunk_types' section in code configuration")
        if 'validation' not in config:
            raise ValueError("Missing 'validation' section in code configuration")
        
        chunk_types = config['chunk_types']
        if 'display_chunk' not in chunk_types:
            raise ValueError("Missing 'display_chunk' in chunk_types configuration")
        if 'executable_chunk' not in chunk_types:
            raise ValueError("Missing 'executable_chunk' in chunk_types configuration")
        
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
    allowed_languages = config.get('validation', {}).get('allowed_languages', ['python', 'javascript', 'html', 'css', 'sql', 'bash', 'yaml', 'json'])
    
    # Use default language if none specified
    if language is None:
        language = 'python'  # Default fallback
    
    # Validate language
    if language not in allowed_languages:
        raise ValueError(f"Language '{language}' not supported. Available: {', '.join(allowed_languages)}")
    
    return language





def _load_layout_code_config(layout_name: str = 'default') -> Dict[str, Any]:
    """Load layout-aware code configuration with spacing and caption_format from layout.
    
    Args:
        layout_name: Name of the layout to load configuration for
        
    Returns:
        Code configuration with layout-specific spacing and caption_format
    """
    try:
        from ePy_docs.core._config import load_layout
        
        # Load base code configuration (chunk_types and validation)
        base_config = _load_code_config()
        
        # Load layout configuration
        layout = load_layout(layout_name, resolve_refs=True)
        
        # Build combined configuration
        config = {
            'chunk_types': base_config['chunk_types'],
            'validation': base_config['validation'],
            'layout_name': layout_name
        }
        
        # Get layout-specific code_chunks configuration
        if 'code_chunks' in layout:
            code_chunks = layout['code_chunks']
            spacing = code_chunks.get('spacing', {'before': '\n\n', 'after': '\n\n'})
            caption_format = code_chunks.get('caption_format', '{caption}')
            
            # Build complete chunk configurations
            config['display_chunk'] = {
                'code_block_format': base_config['chunk_types']['display_chunk']['code_block_format'],
                'spacing': spacing,
                'caption_format': '\n\n' + caption_format + '\n'
            }
            config['executable_chunk'] = {
                'code_block_format': base_config['chunk_types']['executable_chunk']['code_block_format'],
                'spacing': spacing,
                'caption_format': '\n\n' + caption_format + '\n'
            }
        else:
            # Fallback: use default spacing and caption
            default_spacing = {'before': '\n\n', 'after': '\n\n'}
            default_caption = '\n\n{caption}\n'
            
            config['display_chunk'] = {
                'code_block_format': base_config['chunk_types']['display_chunk']['code_block_format'],
                'spacing': default_spacing,
                'caption_format': default_caption
            }
            config['executable_chunk'] = {
                'code_block_format': base_config['chunk_types']['executable_chunk']['code_block_format'],
                'spacing': default_spacing,
                'caption_format': default_caption
            }
        
        return config
        
    except Exception:
        # Fallback to base configuration with defaults
        base_config = _load_code_config()
        default_spacing = {'before': '\n\n', 'after': '\n\n'}
        default_caption = '\n\n{caption}\n'
        
        return {
            'chunk_types': base_config['chunk_types'],
            'validation': base_config['validation'],
            'layout_name': layout_name,
            'display_chunk': {
                'code_block_format': base_config['chunk_types']['display_chunk']['code_block_format'],
                'spacing': default_spacing,
                'caption_format': default_caption
            },
            'executable_chunk': {
                'code_block_format': base_config['chunk_types']['executable_chunk']['code_block_format'],
                'spacing': default_spacing,
                'caption_format': default_caption
            }
        }


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
    
    # Get layout name for consistent visual formatting
    layout_name = config.get('layout_name', 'default')
    
    # Add visual differentiation for PDF/HTML using Quarto callouts
    # This provides clear visual distinction between display and executable chunks
    if chunk_type == 'display':
        # Display chunks get a neutral "note" callout (usually light/white background)
        formatted_code_block = f''':::: {{.callout-note appearance="simple" icon="false"}}

{formatted_code_block}

::::'''
    elif chunk_type == 'executable':
        # Executable chunks get a "tip" callout (usually colored/brown background)
        formatted_code_block = f''':::: {{.callout-tip appearance="simple" icon="false"}}

{formatted_code_block}

::::'''
    
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
    
    # Try to load layout-aware configuration if layout_name is available
    layout_name = config.get('layout_name')
    if layout_name:
        try:
            config = _load_layout_code_config(layout_name)
        except Exception:
            # Fallback to base config with layout name preserved
            pass
    
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