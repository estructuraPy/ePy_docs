"""Notes configuration and callout generation.

Setup Dimension: Centralized cache via _load_cached_files
Appearance Dimension: Organization by layout_styles  
Transparency Dimension: No backward compatibility, no fallbacks
Commerce Dimension: Uses COLORS and TEXT resources through official channels
"""

from typing import Dict, Any
from ePy_docs.files import _load_cached_files
from ePy_docs.components.setup import _resolve_config_path

def get_notes_config(sync_files: bool = False) -> Dict[str, Any]:
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

# Global Note Configuration Cache (TRANSPARENCY DIMENSION)
_notes_config_cache = None
_layout_style_cache = None

def _get_color_from_reference(color_ref: str, layout_style: str, sync_files: bool = False):
    """Get color from layout-specific color reference.
    
    Pure function following TRANSPARENCY DIMENSION principles.
    
    Args:
        color_ref: Color reference key
        layout_style: Layout style name
        sync_files: File synchronization control
        
    Returns:
        RGB color tuple
    """
    from ePy_docs.components.colors import get_colors_config
    colors_config = get_colors_config(sync_files)
    
    # Get layout colors configuration
    if layout_style in colors_config['layout_styles']:
        layout_colors = colors_config['layout_styles'][layout_style]
        
        # Get color reference from layout colors
        if color_ref in layout_colors:
            color_spec = layout_colors[color_ref]
            palette_name = color_spec['palette']
            tone = color_spec['tone']
            
            # Get actual RGB values
            palette = colors_config['palettes'][palette_name]
            return palette[tone]
    
    # Fallback to blues medium if reference not found
    return colors_config['palettes']['blues']['medium']

# Pure Functions for Note Rendering (TRANSPARENCY DIMENSION)

def create_note_html(content: str, note_type: str, layout_style: str = "corporate", title: str = None, sync_files: bool = False):
    """Create HTML for callout display using layout_styles configuration.
    
    Pure function following TRANSPARENCY DIMENSION principles.
    
    Args:
        content: Content of the callout
        note_type: Type of callout
        layout_style: Layout style to use
        title: Optional title
        sync_files: File synchronization control
        
    Returns:
        HTML string for display
    """
    config = get_notes_config(sync_files)
    
    # Get layout-specific configuration
    layout_config = config['layout_styles'][layout_style]
    
    # Validate note_type exists in layout configuration
    if note_type not in layout_config:
        # Fallback to 'note' if type not found
        note_type = 'note'
        
    note_config = layout_config[note_type]
    
    # Get colors from configuration
    main_color_rgb = _get_color_from_reference(note_config['color_ref'], layout_style, sync_files)
    border_color_rgb = _get_color_from_reference(note_config['border_ref'], layout_style, sync_files)
    bg_alpha = note_config['bg_alpha']
    
    # Convert RGB to CSS format
    bg_color = f"rgba({main_color_rgb[0]}, {main_color_rgb[1]}, {main_color_rgb[2]}, {bg_alpha})"
    border_color = f"rgb({border_color_rgb[0]}, {border_color_rgb[1]}, {border_color_rgb[2]})"
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

def create_note_markdown(content: str, note_type: str, title: str = None):
    """Create Quarto markdown for callout.
    
    Pure function following TRANSPARENCY DIMENSION principles.
    
    Args:
        content: Content of the callout
        note_type: Type of callout
        title: Optional title
        
    Returns:
        Quarto markdown string
    """
    if title:
        return f"\n\n::: {{{note_type}}}\n## {title}\n{content}\n:::\n\n"
    else:
        return f"\n\n::: {{{note_type}}}\n{content}\n:::\n\n"

def display_callout(content: str, note_type: str, layout_style: str = "corporate", title: str = None, sync_files: bool = False):
    """Display callout visually in notebook or return HTML.
    
    Pure function following TRANSPARENCY DIMENSION principles.
    
    Args:
        content: Content of the callout
        note_type: Type of callout (tip, warning, note, etc.)
        layout_style: Layout style to use
        title: Optional title for the callout
        sync_files: File synchronization control
    """
    html = create_note_html(content, note_type, layout_style, title, sync_files)
    
    try:
        # Try to display in Jupyter/IPython environment
        from IPython.display import HTML, display
        display(HTML(html))
    except ImportError:
        # If not in Jupyter, return HTML for other uses
        print(f"Note ({note_type}): {title if title else ''}")
        print(content)
        return html

# Legacy Compatibility Class (TRANSPARENCY DIMENSION)

class NoteRenderer:
    """Legacy wrapper for NoteRenderer functionality.
    
    Maintains backward compatibility while promoting pure functions.
    All methods delegate to pure functions following TRANSPARENCY DIMENSION.
    """
    """Legacy wrapper for NoteRenderer functionality.
    
    Maintains backward compatibility while promoting pure functions.
    All methods delegate to pure functions following TRANSPARENCY DIMENSION.
    """
    
    def __init__(self, layout_style: str = "corporate", sync_files: bool = False):
        """Initialize note renderer.
        
        Args:
            layout_style: One of 8 universal layout styles
            sync_files: File synchronization control
        """
        self.layout_style = layout_style
        self.sync_files = sync_files
        self.config = get_notes_config(sync_files)
        
        # Validate layout_style exists
        if layout_style not in self.config['layout_styles']:
            raise ValueError(f"Layout style '{layout_style}' not found in notes configuration")
    
    def display_callout(self, content: str, note_type: str, title: str = None):
        """Legacy wrapper for display_callout function."""
        return display_callout(content, note_type, self.layout_style, title, self.sync_files)
    
    def create_note_html(self, content: str, note_type: str, title: str = None):
        """Legacy wrapper for create_note_html function."""
        return create_note_html(content, note_type, self.layout_style, title, self.sync_files)
    
    def create_note_markdown(self, content: str, note_type: str, title: str = None):
        """Legacy wrapper for create_note_markdown function."""
        return create_note_markdown(content, note_type, title)
