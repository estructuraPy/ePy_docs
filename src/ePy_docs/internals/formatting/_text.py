"""
TEXT Module - Typography and text formatting

Configuration: Centralized cache via _load_cached_files
Styling: Organization by layout_styles
Compatibility: No backward compatibility, no fallbacks
"""

from typing import Dict, Any
from ePy_docs.internals.data_processing._data import load_cached_files
from ePy_docs.config.setup import _resolve_config_path
from typing import Dict, Any, Optional
import re

def get_text_config() -> Dict[str, Any]:
    """Get text configuration from centralized config."""
    from ePy_docs.config.setup import get_config_section
    return get_config_section('text')


def add_header_to_content(text: str, level: int = 1, color: Optional[str] = None) -> str:
    """Generate header markdown.
    
    Args:
        text: Header text
        level: Header level (1-6)
        color: Optional color (ignored in pure markdown)
        
    Returns:
        Markdown header content
    """
    if level < 1 or level > 6:
        level = 1
    
    header_prefix = "#" * level
    return f"\n{header_prefix} {text}\n\n"


def add_h1_to_content(text: str, color: Optional[str] = None) -> str:
    """Generate H1 header markdown."""
    return add_header_to_content(text, 1, color)


def add_h2_to_content(text: str, color: Optional[str] = None) -> str:
    """Generate H2 header markdown."""
    return add_header_to_content(text, 2, color)


def add_h3_to_content(text: str, add_newline: bool = True, color: Optional[str] = None) -> str:
    """Generate H3 header markdown."""
    content = f"\n### {text}"
    if add_newline:
        content += "\n\n"
    else:
        content += "\n"
    return content


def add_text_to_content(content: str) -> str:
    """Generate text content with mathematical notation.
    
    Args:
        content: Text content
        sync_files: Control cache synchronization
        
    Returns:
        Processed markdown content
    """
    if not isinstance(content, str):
        content = str(content)
    
    processed_content = content
    
    # Process mathematical notation using FORMAT module
    try:
        from ePy_docs.internals.formatting._format import format_superscripts
        
        # First, process ${variable} patterns
        def process_math_variable(match):
            variable_content = match.group(1)
            # For variables in math expressions, just clean the variable name
            return f"${variable_content}$"
        
        # Process ${variable} patterns
        processed_content = re.sub(r'\$\{([^}]+)\}', process_math_variable, processed_content)
        
        # Apply superscript formatting only to text OUTSIDE of LaTeX equations
        parts = re.split(r'(\$[^$]*\$)', processed_content)
        
        formatted_parts = []
        for i, part in enumerate(parts):
            if i % 2 == 0:  # Even indices are regular text
                formatted_part = format_superscripts(part, 'html')
                formatted_parts.append(formatted_part)
            else:  # Odd indices are LaTeX equations - preserve them exactly
                formatted_parts.append(part)
        
        processed_content = ''.join(formatted_parts)
        
    except Exception as e:
        # If mathematical processing fails, continue without it
        pass
    
    # Apply bullet conversion
    processed_content = processed_content.replace('• ', '- ')
    
    # Preserve line breaks and add proper spacing
    if '\n' in processed_content:
        return f"{processed_content}\n\n"
    else:
        return f"{processed_content}\n\n"


def add_content_to_buffer(content: str) -> str:
    """Add plain content preserving original formatting.
    
    Args:
        content: Content to add
        
    Returns:
        Content as-is for buffer appending
    """
    return content if content else ""


def process_text_content(text: str) -> str:
    """Centralized text processing for consistent markdown.
    
    Args:
        text: Input text
        sync_files: Control cache synchronization
        
    Returns:
        Processed text with consistent formatting
    """
    if not text:
        return ""
    
    if not isinstance(text, str):
        text = str(text)
        
    result = text.strip()
    
    # Process mathematical notation
    try:
        from ePy_docs.internals.formatting._format import format_superscripts
        
        def process_math_variable(match):
            variable_content = match.group(1)
            formatted_content = format_superscripts(variable_content, 'html')
            return f"${formatted_content}$"
        
        # Process ${variable} patterns
        result = re.sub(r'\$\{([^}]+)\}', process_math_variable, result)
        
        # Apply general superscript processing
        result = format_superscripts(result, 'html')
    except Exception:
        pass
    
    # Enhanced header processing
    for i in range(6, 0, -1):
        header_pattern = r'(^|\n)#{' + str(i) + r'}\s+(.+?)(\n|$)'
        replacement = r'\1' + '#' * i + r' \2\n\n'
        result = re.sub(header_pattern, replacement, result)
    
    # Preserve image syntax with better spacing
    result = re.sub(r'([^\n])(!\[.*?\]\(.*?\)(\s*\{[^}]*\})?)', r'\1\n\n\2', result)
    result = re.sub(r'(!\[.*?\]\(.*?\)(\s*\{[^}]*\})?)([^\n])', r'\1\n\n\3', result)
    
    # Normalize line endings
    result = re.sub(r'\r\n', '\n', result)
    
    # Clean up multiple blank lines
    result = re.sub(r'\n{3,}', '\n\n', result)
    
    # Clean trailing whitespace
    result = re.sub(r'[ \t]+$', '', result, flags=re.MULTILINE)
    
    return result if result.strip() else result.strip()


def format_list(items: list, ordered: bool = False) -> str:
    """
    Format a list as markdown (ordered or unordered).
    
    Args:
        items: List of strings to format
        ordered: If True, creates numbered list; if False, creates bulleted list
        
    Returns:
        Formatted markdown list string
        
    Example:
        >>> format_list(["Item 1", "Item 2"], ordered=False)
        '\\n- Item 1\\n- Item 2\\n\\n'
        >>> format_list(["First", "Second"], ordered=True)
        '\\n1. First\\n2. Second\\n\\n'
    """
    if ordered:
        list_content = "\n".join(f"{i+1}. {item}" for i, item in enumerate(items))
    else:
        list_content = "\n".join(f"- {item}" for item in items)
    
    return f"\n{list_content}\n\n"
