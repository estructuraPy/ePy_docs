"""
Reference and citation formatting for ePy_docs.

This module provides functionality to format cross-references 
and citations in documentation.
"""

from typing import Optional


def format_cross_reference(ref_type: str, ref_id: str, custom_text: Optional[str] = None) -> str:
    """Format cross-reference to figure, table, equation, or note.
    
    Args:
        ref_type: Type of reference ('fig', 'tbl', 'eq', 'note')
        ref_id: Reference ID
        custom_text: Optional custom text for the reference
        
    Returns:
        Formatted cross-reference
        
    Raises:
        ValueError: If ref_type is invalid
    """
    if ref_type == 'note':
        # Note references are handled by the note renderer
        # This will be handled in the calling method
        return ""
    elif ref_type in ['fig', 'tbl', 'eq']:
        if custom_text:
            return f"[{custom_text}](#{ref_id})"
        else:
            return f"@{ref_id}"
    else:
        raise ValueError(f"Invalid reference type: {ref_type}")


def format_citation(citation_key: str, page: Optional[str] = None) -> str:
    """Format inline citation.
    
    Args:
        citation_key: Citation key from bibliography
        page: Optional page number
        
    Returns:
        Formatted citation
    """
    if page:
        return f"[@{citation_key}, p. {page}]"
    else:
        return f"[@{citation_key}]"
