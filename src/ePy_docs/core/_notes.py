"""Note generation utilities for ePy_docs.

SOLID-compliant note generation with configuration-driven type mapping.
Version: 3.0.0 - Zero hardcoding, zero backward compatibility
"""

from typing import Tuple


# Valid Quarto callout types (fixed)
VALID_NOTE_TYPES = {'note', 'warning', 'caution', 'important', 'tip'}

# Common type aliases for better UX
TYPE_ALIASES = {
    'success': 'tip',      # Green/positive callout
    'error': 'caution',    # Red/negative callout
    'danger': 'caution',   # Red/negative callout
    'info': 'note',        # Blue/informational callout
    'hint': 'tip',         # Green/helpful callout
    'alert': 'warning',    # Orange/attention callout
}

def add_note_to_content(content: str, title: str = None, note_type: str = "note", note_counter: int = 1) -> Tuple[str, int]:
    """Generate Quarto callout markdown for a note.
    
    Args:
        content: Note content text
        title: Optional note title
        note_type: Note type (note, warning, caution, important, tip) or alias
                  (success, error, danger, info, hint, alert)
        note_counter: Current note counter (preserved for caller compatibility)
        
    Returns:
        Tuple of (callout_markdown, note_counter)
        
    Raises:
        ValueError: If content is empty or note_type is invalid
    """
    if not content:
        return "", note_counter
    
    # Normalize and resolve aliases
    normalized_type = note_type.lower().strip()
    if normalized_type in TYPE_ALIASES:
        normalized_type = TYPE_ALIASES[normalized_type]
    
    # Validate note type against fixed Quarto types
    if normalized_type not in VALID_NOTE_TYPES:
        allowed = sorted(VALID_NOTE_TYPES | set(TYPE_ALIASES.keys()))
        raise ValueError(
            f"Invalid note_type '{note_type}'. "
            f"Allowed types: {', '.join(allowed)}"
        )
    
    callout_content = ""
    
    # Start minipage for PDF to prevent page breaks
    callout_content += "```{=latex}\n"
    callout_content += "\\begin{minipage}{\\linewidth}\n"
    callout_content += "```\n\n"
    
    callout_content += f":::{{.callout-{normalized_type}}}\n"
    
    if title:
        callout_content += f"## {title}\n\n"
    
    callout_content += f"{content}\n"
    callout_content += ":::\n\n"
    
    # End minipage for PDF
    callout_content += "```{=latex}\n"
    callout_content += "\\end{minipage}\n"
    callout_content += "```\n\n"
    
    return callout_content, note_counter

