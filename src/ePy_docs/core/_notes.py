"""Note generation utilities for ePy_docs.

SOLID-compliant note generation with configuration-driven type mapping.
Version: 3.0.0 - Zero hardcoding, zero backward compatibility
"""

from typing import Tuple


def add_note_to_content(content: str, title: str = None, note_type: str = "note", note_counter: int = 1) -> Tuple[str, int]:
    """Generate Quarto callout markdown for a note.
    
    Args:
        content: Note content text
        title: Optional note title
        note_type: Note type (note, warning, error, tip, etc.)
        note_counter: Current note counter (preserved for caller compatibility)
        
    Returns:
        Tuple of (callout_markdown, note_counter)
        
    Raises:
        ValueError: If content is empty or type_mapping not in configuration
    """
    if not content:
        return "", note_counter
    
    # Load type mapping from configuration
    from ePy_docs.core._config import get_config_section
    config = get_config_section('notes')
    
    if 'type_mapping' not in config:
        raise ValueError(
            "Configuration error: 'type_mapping' not found in notes.epyson. "
            "Expected structure: {'type_mapping': {'note': 'note', 'warning': 'warning', ...}}"
        )
    
    type_mapping = config['type_mapping']
    
    # Validate note type exists in mapping
    if note_type not in type_mapping:
        raise ValueError(
            f"Invalid note_type '{note_type}'. "
            f"Allowed types: {', '.join(type_mapping.keys())}"
        )
    
    quarto_type = type_mapping[note_type]
    callout_content = f"\n\n:::{{.callout-{quarto_type}}}\n"
    
    if title:
        callout_content += f"## {title}\n\n"
    
    callout_content += f"{content}\n"
    callout_content += ":::\n\n"
    
    return callout_content, note_counter

