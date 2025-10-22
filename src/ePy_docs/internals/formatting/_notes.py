from typing import Dict, Any, Optional
from ePy_docs.internals.data_processing._data import load_cached_files
from ePy_docs.config.setup import _resolve_config_path

def get_notes_config() -> Dict[str, Any]:
    """Get notes configuration."""
    try:
        from ePy_docs.internals.data_processing._data import load_cached_files
    except ImportError:
        raise ImportError("ePy_files library is required. Install with: pip install ePy_files")
        
    config_path = _resolve_config_path('components/notes')
    return load_cached_files(config_path)

def add_note_to_content(content: str, title: str = None, note_type: str = "note") -> str:
    """Generate note callout markdown."""
    if not content:
        return ""
    
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
    
    return callout_content

def add_warning_to_content(content: str, title: str = None) -> str:
    """Generate warning callout."""
    return add_note_to_content(content, title, "warning")

def add_error_to_content(content: str, title: str = None) -> str:
    """Generate error callout.""" 
    return add_note_to_content(content, title, "error")

def add_success_to_content(content: str, title: str = None) -> str:
    """Generate success callout."""
    return add_note_to_content(content, title, "success")

def add_tip_to_content(content: str, title: str = None) -> str:
    """Generate tip callout."""
    return add_note_to_content(content, title, "tip")

def add_caution_to_content(content: str, title: str = None) -> str:
    """Generate caution callout."""
    return add_note_to_content(content, title, "caution")

def add_important_to_content(content: str, title: str = None) -> str:
    """Generate important callout."""
    return add_note_to_content(content, title, "important")

def add_information_to_content(content: str, title: str = None) -> str:
    """Generate information callout."""
    return add_note_to_content(content, title, "information")

def add_recommendation_to_content(content: str, title: str = None) -> str:
    """Generate recommendation callout."""
    return add_note_to_content(content, title, "recommendation")

def add_advice_to_content(content: str, title: str = None) -> str:
    """Generate advice callout."""
    return add_note_to_content(content, title, "advice")

def add_risk_to_content(content: str, title: str = None) -> str:
    """Generate risk callout."""
    return add_note_to_content(content, title, "risk")

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