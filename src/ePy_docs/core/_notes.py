from typing import Dict, Any, Optional, Tuple

def get_notes_config() -> Dict[str, Any]:
    """Get notes configuration."""
    try:
        from ePy_docs.core._config import get_config_section
        return get_config_section('notes')
    except ImportError:
        raise ImportError("Configuration system not available. Please ensure ePy_docs is properly installed.")

def add_note_to_content(content: str, title: str = None, note_type: str = "note", note_counter: int = 1) -> Tuple[str, int]:
    """Generate note callout markdown and return new counter."""
    if not content:
        return "", note_counter
    
    type_mapping = {
        'note': 'note',
        'information': 'note', 
        'warning': 'warning',
        'risk': 'warning',
        'error': 'caution',
        'caution': 'caution',
        'success': 'important',
        'important': 'important',
        'tip': 'tip',
        'recommendation': 'tip',
        'advice': 'tip'
    }
    
    quarto_type = type_mapping.get(note_type, 'note')
    callout_content = f"\n\n:::{{.callout-{quarto_type}}}\n"
    
    if title:
        callout_content += f"## {title}\n\n"
    
    callout_content += f"{content}\n"
    callout_content += ":::\n\n"
    
    # Return same counter (caller already passed counter + 1)
    return callout_content, note_counter

def add_warning_to_content(content: str, title: str = None, note_counter: int = 1) -> Tuple[str, int]:
    """Generate warning callout."""
    return add_note_to_content(content, title, "warning", note_counter)

def add_error_to_content(content: str, title: str = None, note_counter: int = 1) -> Tuple[str, int]:
    """Generate error callout.""" 
    return add_note_to_content(content, title, "error", note_counter)

def add_success_to_content(content: str, title: str = None, note_counter: int = 1) -> Tuple[str, int]:
    """Generate success callout."""
    return add_note_to_content(content, title, "success", note_counter)

def add_tip_to_content(content: str, title: str = None, note_counter: int = 1) -> Tuple[str, int]:
    """Generate tip callout."""
    return add_note_to_content(content, title, "tip", note_counter)

def add_caution_to_content(content: str, title: str = None, note_counter: int = 1) -> Tuple[str, int]:
    """Generate caution callout."""
    return add_note_to_content(content, title, "caution", note_counter)

def add_important_to_content(content: str, title: str = None, note_counter: int = 1) -> Tuple[str, int]:
    """Generate important callout."""
    return add_note_to_content(content, title, "important", note_counter)

def add_information_to_content(content: str, title: str = None, note_counter: int = 1) -> Tuple[str, int]:
    """Generate information callout."""
    return add_note_to_content(content, title, "information", note_counter)

def add_recommendation_to_content(content: str, title: str = None, note_counter: int = 1) -> Tuple[str, int]:
    """Generate recommendation callout."""
    return add_note_to_content(content, title, "recommendation", note_counter)

def add_advice_to_content(content: str, title: str = None, note_counter: int = 1) -> Tuple[str, int]:
    """Generate advice callout."""
    return add_note_to_content(content, title, "advice", note_counter)

def add_risk_to_content(content: str, title: str = None, note_counter: int = 1) -> Tuple[str, int]:
    """Generate risk callout."""
    return add_note_to_content(content, title, "risk", note_counter)

def create_note_markdown(content: str, note_type: str, title: str = None) -> str:
    """Centralized note creation."""
    return add_note_to_content(content, title, note_type)

class NoteRenderer:
    """Legacy wrapper maintaining backward compatibility."""
    
    def __init__(self):
        self.note_counter = 0
    
    def create_note_markdown(self, content: str, note_type: str, title: str = None) -> str:
        """Legacy method delegating to module functions."""
        return create_note_markdown(content, note_type, title)