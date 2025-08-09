"""Note rendering system for reports and presentations.

Provides shared note rendering capabilities including different note types
(note, warning, error, success, tip) with consistent styling and Quarto callout support.
"""

from typing import Optional, Dict, Any, List
import json
import os

from ePy_docs.core.content import ContentProcessor
from ePy_docs.components.colors import _load_cached_colors


class NoteRenderer:
    """Renderer for different types of notes with consistent styling."""
    
    def __init__(self):
        self.note_counter = 0
        self._cross_references = {}
    
    def _load_quarto_config(self) -> Dict[str, Any]:
        """Load quarto configuration from quarto.json - no fallbacks."""
        config_path = os.path.join(os.path.dirname(__file__), '..', 'formats', 'quarto.json')
        
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _load_color_config(self) -> Dict[str, Any]:
        """Load color configuration from colors.json - no fallbacks."""
        return _load_cached_colors()
    
    def _get_note_colors(self, note_type: str) -> Dict[str, Any]:
        """Get color configuration for specific note type."""
        colors_config = self._load_color_config()
        return colors_config['reports']['notes'][note_type]
    
    def _rgb_to_css(self, rgb_list: List[int]) -> str:
        """Convert RGB list to CSS rgb() string."""
        return f"rgb({rgb_list[0]}, {rgb_list[1]}, {rgb_list[2]})"
    
    def _generate_custom_css(self, note_type: str, color_config: Dict[str, Any]) -> str:
        """Generate custom CSS for callout styling."""
        background = self._rgb_to_css(color_config['background'])
        border = self._rgb_to_css(color_config['border'])
        text_color = self._rgb_to_css(color_config['text_color'])
        icon_color = self._rgb_to_css(color_config['icon_color'])
        
        css_class = f"callout-{note_type}-custom"
        
        return f"""
<style>
.{css_class} {{
    background-color: {background};
    border-left: 4px solid {border};
    border-radius: 0.25rem;
    padding: 1rem;
    margin: 1rem 0;
    color: {text_color};
}}
.{css_class} .callout-title {{
    color: {icon_color};
    font-weight: bold;
}}
</style>
"""
    
    def create_quarto_callout(self, content: str, note_type: str = "note", 
                            title: Optional[str] = None, ref_id: Optional[str] = None,
                            collapse: bool = False, icon: bool = True, 
                            appearance: str = "default") -> Dict[str, str]:
        """Create a Quarto callout block using only JSON configuration.
        
        Args:
            content: Callout content
            note_type: Type of callout - must exist in JSON config
            title: Optional title for the callout
            ref_id: Optional reference ID for cross-referencing
            collapse: Whether the callout should be collapsible
            icon: Whether to show the callout icon
            appearance: Callout appearance style
            
        Returns:
            Dictionary with callout markdown and metadata
        """
        self.note_counter += 1
        
        # Load configuration from JSON - fail if not found
        quarto_config = self._load_quarto_config()
        callout_config = quarto_config['callouts'][note_type]  # Will KeyError if not found
        
        # Get color configuration from colors.json
        color_config = self._get_note_colors(note_type)
        
        # Use only config values - no parameter overrides
        collapse = callout_config['collapse']
        icon = callout_config['icon']
        appearance = callout_config['appearance']
        
        # Get quarto type from config - no hardcoded mapping
        quarto_type = quarto_config['quarto_callout_types'][note_type]
        
        # Generate reference ID if not provided
        if ref_id is None:
            ref_id = f"{note_type}-{self.note_counter}"
        
        # Generate title if not provided - use generic title without counter
        if title is None:
            title_config = quarto_config['callout_titles'][note_type]
            title = title_config  # Don't add counter to title display
        
        # Build callout options from config
        options = []
        if collapse:
            options.append('collapse="true"')
        if not icon:
            options.append('icon="false"')
        if appearance != 'default':
            options.append(f'appearance="{appearance}"')
        
        options_str = ' '.join(options)
        if options_str:
            options_str = ' ' + options_str
        
        # Format content
        formatted_content = self.format_note_content(
            ContentProcessor.smart_content(content), 
            note_type
        )
        
        # Generate custom CSS for colors
        custom_css = self._generate_custom_css(note_type, color_config)
        css_class = f"callout-{note_type}-custom"
        
        # Build callout markdown with custom styling
        callout_markdown = custom_css
        callout_markdown += f'::: {{.callout-{quarto_type} .{css_class}{options_str}}}\n'
        
        # Add title with icon from color config
        icon_symbol = color_config.get('icon', '').strip('[]')
        callout_markdown += f"## {icon_symbol} {title}\n"
        
        if formatted_content.strip():
            callout_markdown += formatted_content.rstrip() + "\n"
        
        callout_markdown += "\n:::\n"
        
        # Store reference for cross-referencing
        self._cross_references[ref_id] = {
            'type': note_type,
            'title': title,
            'number': self.note_counter
        }
        
        return {
            'markdown': callout_markdown,
            'ref_id': ref_id,
            'title': title,
            'type': note_type,
            'number': self.note_counter
        }
    
    def format_note_content(self, content: str, note_type: str = "note") -> str:
        """Format note content for display.
        
        Args:
            content: Raw note content
            note_type: Type of note
            
        Returns:
            Formatted content
        """
        # Para callouts, preservar completamente la estructura definida por el usuario
        # NO hacer ningún tipo de limpieza que pueda alterar la estructura
        if not isinstance(content, str):
            return str(content)
        
        # Solo remover espacios al final y principio del contenido completo, 
        # pero preservar toda la estructura interna
        return content.strip()
    
    def get_note_style(self, note_type: str) -> Dict[str, Any]:
        """Get styling configuration for note type.
        
        Args:
            note_type: Type of note
            
        Returns:
            Style configuration
        """
        return ContentProcessor.get_note_config(note_type) or {}
    
    def increment_counter(self) -> int:
        """Increment and return note counter.
        
        Returns:
            Current note counter value
        """
        self.note_counter += 1
        return self.note_counter
    
    def create_cross_reference(self, ref_id: str, custom_text: str = None) -> str:
        """Create a cross-reference to a note callout using JSON config.
        
        Args:
            ref_id: Reference ID of the callout
            custom_text: Optional custom text for the reference
            
        Returns:
            Cross-reference markdown
        """
        if ref_id not in self._cross_references:
            raise KeyError(f"Reference ID '{ref_id}' not found")
        
        ref_info = self._cross_references[ref_id]
        
        if custom_text is None:
            # Get title from config
            quarto_config = self._load_quarto_config()
            type_name = quarto_config['callout_titles'][ref_info['type']]
            custom_text = f"{type_name} {ref_info['number']}"
        
        return f"{{{custom_text}}} (@{ref_id})"
    
    def get_cross_references_list(self) -> Dict[str, Dict[str, Any]]:
        """Get a list of all cross-references created.
        
        Returns:
            Dictionary with all cross-references
        """
        return self._cross_references.copy()
