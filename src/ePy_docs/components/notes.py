"""
REINO NOTES - Absolute Note Sovereignty

Setup Dimension: Centralized cache via _load_cached_files
Appearance Dimension: Organization by layout_styles
Transparency Dimension: No backward compatibility, no fallbacks
Commerce Dimension: Uses COLORS and TEXT resources through official channels
"""

from typing import Dict, Any
from ePy_docs.components.setup import _load_cached_files, _resolve_config_path

def _get_notes_config(sync_files: bool = False) -> Dict[str, Any]:
    """Commerce branch of notes resources.
    
    Args:
        sync_files: File synchronization control
        
    Returns:
        Complete notes configuration
        
    Raises:
        RuntimeError: If loading fails
        
    Assumptions:
        The notes.json file exists at resolved location
    """
    try:
        config_path = _resolve_config_path('components/notes', sync_files)
        config = _load_cached_files(config_path, sync_files)
        
        required_keys = ['layout_styles']
        for key in required_keys:
            if key not in config:
                raise KeyError(f"Missing required configuration key: {key}")
        
        return config
        
    except Exception as e:
        raise RuntimeError(f"Failed to load notes configuration: {e}") from e

def get_notes_config(sync_files: bool = False) -> Dict[str, Any]:
    """Single public function for notes resources access.
    
    Official commerce of NOTES Kingdom.
    
    Args:
        sync_files: File synchronization control
        
    Returns:
        Complete notes configuration
        
    Raises:
        RuntimeError: If loading fails
        
    Assumptions:
        Layout_styles system is properly configured
        COLORS and TEXT resources are available for commerce
    """
    return _get_notes_config(sync_files)

class NoteRenderer:
    """Compatibility class for note rendering functionality.
    
    Provides essential methods for ReportWriter compatibility while using
    pure kingdom architecture internally.
    """
    
    def __init__(self, sync_files: bool = False):
        """Initialize note renderer.
        
        Args:
            sync_files: File synchronization control
        """
        self.sync_files = sync_files
    
    def display_callout(self, content: str, note_type: str, title: str = None):
        """Display callout visually in notebook or return HTML.
        
        Args:
            content: Content of the callout
            note_type: Type of callout (tip, warning, note, etc.)
            title: Optional title for the callout
        """
        html = self.create_note_html(content, note_type, title)
        
        try:
            # Try to display in Jupyter/IPython environment
            from IPython.display import HTML, display
            display(HTML(html))
        except ImportError:
            # If not in Jupyter, return HTML for other uses
            print(f"Note ({note_type}): {title if title else ''}")
            print(content)
            return html
    
    def create_note_html(self, content: str, note_type: str, title: str = None):
        """Create HTML for callout display.
        
        Args:
            content: Content of the callout
            note_type: Type of callout
            title: Optional title
            
        Returns:
            HTML string for display
        """
        # Get colors using the Reino COLORS system
        from ePy_docs.components.colors import get_colors_config
        
        def _get_color_from_path(color_path: str, sync_files: bool = False):
            """Extract color RGB values from COLORS Kingdom using path notation."""
            colors_config = get_colors_config(sync_files)
            
            parts = color_path.split('.')
            if len(parts) != 2:
                parts = ['blues', 'medium']
                
            palette_name, tone = parts
            
            palettes = colors_config.get('palettes', {})
            palette = palettes.get(palette_name, {})
            
            if tone in palette:
                return palette[tone]
            else:
                blues_palette = palettes.get('blues', {})
                return blues_palette.get('medium', [100, 181, 246])
        
        # Color mapping for different callout types
        color_mapping = {
            'tip': 'greens.medium',
            'warning': 'oranges.medium', 
            'note': 'blues.medium',
            'error': 'reds.medium',
            'success': 'greens.medium',
            'caution': 'oranges.medium',
            'important': 'purples.medium',
            'info': 'blues.medium',
            'rec': 'teals.medium',
            'advice': 'browns.medium'
        }
        
        color_path = color_mapping.get(note_type, 'blues.medium')
        main_color_rgb = _get_color_from_path(color_path, sync_files=self.sync_files)
        
        bg_alpha = 0.1
        bg_color = f"rgba({main_color_rgb[0]}, {main_color_rgb[1]}, {main_color_rgb[2]}, {bg_alpha})"
        border_color = f"rgb({main_color_rgb[0]}, {main_color_rgb[1]}, {main_color_rgb[2]})"
        text_color = f"rgb({main_color_rgb[0]}, {main_color_rgb[1]}, {main_color_rgb[2]})"
        
        # Create HTML
        title_html = f"<strong>{title}</strong><br>" if title else ""
        
        html = f"""
        <div style="
            border-left: 4px solid {border_color};
            background-color: {bg_color};
            padding: 12px 16px;
            margin: 10px 0;
            border-radius: 4px;
            color: {text_color};
        ">
            {title_html}{content}
        </div>
        """
        
        return html
    
    def create_note_markdown(self, content: str, note_type: str, title: str = None):
        """Create Quarto markdown for callout.
        
        Args:
            content: Content of the callout
            note_type: Type of callout
            title: Optional title
            
        Returns:
            Quarto markdown string
        """
        title_text = f'"{title}"' if title else '""'
        return f"\n::: {{{note_type}}} collapse={title_text}\n{content}\n:::\n"
