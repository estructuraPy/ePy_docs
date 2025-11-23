"""
Code chunk formatting for ePy_docs.

Provides functionality to format code chunks for documentation,
including display-only and executable code blocks.

Design: Configuration-driven architecture - loads chunk_types from layouts.
Accepts all Quarto-supported languages without restriction.
"""
from typing import Optional, Dict, Any


def get_available_languages() -> list:
    """Get available programming languages for code chunks.
    
    Returns:
        List indicating all Quarto-supported languages are accepted.
        
    Note:
        This function returns a placeholder list. All Quarto-supported
        languages are accepted without validation.
        
    Example:
        languages = get_available_languages()
        print("All Quarto languages supported")
    """
    return ["all-quarto-languages"]


def _validate_inputs(code: str, language: Optional[str], chunk_type: str) -> str:
    """Validate and normalize inputs for code chunk formatting.
    
    Args:
        code: Source code content to validate
        language: Programming language identifier (all Quarto languages accepted)
        chunk_type: Type of chunk ('display' or 'executable')
        
    Returns:
        Normalized language identifier
        
    Raises:
        ValueError: If code is None or empty
        
    Note:
        Language validation removed - all Quarto-supported languages accepted.
    """
    if code is None or not code or not code.strip():
        raise ValueError("Code content is required")
    
    # Use default language if none specified
    if language is None:
        language = 'python'  # Default fallback
    
    # No language validation - accept all Quarto-supported languages
    return language


def _load_layout_code_config(layout_name: str = 'classic') -> Dict[str, Any]:
    """Load layout-aware code configuration with chunk_types, spacing and caption_format.
    
    Args:
        layout_name: Name of the layout to load configuration for
        
    Returns:
        Code configuration with chunk_types and layout-specific settings
    """
    try:
        from ePy_docs.core._config import load_layout
        
        # Load layout configuration
        layout = load_layout(layout_name, resolve_refs=True)
        
        # Get chunk_types from layout
        if 'chunk_types' not in layout:
            raise ValueError(f"Missing 'chunk_types' in layout '{layout_name}'")
        
        chunk_types = layout['chunk_types']
        
        # Build combined configuration
        config = {
            'chunk_types': chunk_types,
            'layout_name': layout_name
        }
        
        # Get layout-specific code_chunks configuration
        if 'code_chunks' in layout:
            code_chunks = layout['code_chunks']
            spacing = code_chunks.get('spacing', {'before': '\n\n', 'after': '\n\n'})
            caption_format = code_chunks.get('caption_format', '{caption}')
            
            # Build complete chunk configurations
            config['display_chunk'] = {
                'code_block_format': chunk_types['display_chunk']['code_block_format'],
                'spacing': spacing,
                'caption_format': '\n\n' + caption_format + '\n'
            }
            config['executable_chunk'] = {
                'code_block_format': chunk_types['executable_chunk']['code_block_format'],
                'spacing': spacing,
                'caption_format': '\n\n' + caption_format + '\n'
            }
        else:
            # Fallback: use default spacing and caption
            default_spacing = {'before': '\n\n', 'after': '\n\n'}
            default_caption = '\n\n{caption}\n'
            
            config['display_chunk'] = {
                'code_block_format': chunk_types['display_chunk']['code_block_format'],
                'spacing': default_spacing,
                'caption_format': default_caption
            }
            config['executable_chunk'] = {
                'code_block_format': chunk_types['executable_chunk']['code_block_format'],
                'spacing': default_spacing,
                'caption_format': default_caption
            }
        
        return config
        
    except Exception as e:
        raise RuntimeError(f"Failed to load code configuration from layout '{layout_name}': {e}")


def _format_code_chunk(code: str, language: str, chunk_type: str, config: Dict[str, Any]) -> str:
    """Format a code chunk with universal styling that works in both HTML and PDF.
    
    Args:
        code: Source code content (already validated)
        language: Programming language identifier (already validated)
        chunk_type: Type of chunk ('display' or 'executable')
        config: Configuration dictionary with layout information
        
    Returns:
        Formatted code block using Quarto callouts for universal compatibility
    """
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
    layout_name = config.get('layout_name', 'classic')
    
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


def format_code_chunk(code: str, language: Optional[str], chunk_type: str, caption: Optional[str] = None, layout_name: str = 'classic', counter: int = 1) -> str:
    """Format a code chunk for documentation.
    
    Args:
        code: Source code content to format
        language: Programming language identifier (all Quarto languages accepted)
        chunk_type: Type of chunk ('display' or 'executable')
        caption: Optional caption text
        layout_name: Layout name to load chunk_types from
        counter: Counter for caption numbering
        
    Returns:
        Formatted markdown code block
        
    Raises:
        ValueError: If code is empty
        TypeError: If code is None
    """
    # Load layout-aware configuration
    config = _load_layout_code_config(layout_name)
    
    # Validate inputs and get normalized language
    validated_language = _validate_inputs(code, language, chunk_type)
    
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
