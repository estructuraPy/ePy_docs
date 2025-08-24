"""Note rendering system for reports and presentations.

Provides shared note rendering capabilities including different note types
(note, warning, error, success, tip) with consistent styling and Quarto callout support.
"""

from typing import Optional, Dict, Any, List
import json
import os

from ePy_docs.core.setup import _load_cached_config


def get_layout_note_style(layout_name: str = None) -> Dict[str, Any]:
    """Get note styling configuration for a specific layout.
    
    Args:
        layout_name: Name of the layout (if None, gets from current report config)
        
    Returns:
        Dictionary with note styling configuration for the layout
    """
    if layout_name is None:
        # Get current layout from report configuration using unified system
        from ePy_docs.core.setup import _load_cached_config
        report_config = _load_cached_config('report')
        
        if 'default_layout' not in report_config:
            raise RuntimeError("Report configuration missing default_layout")
        layout_name = report_config['default_layout']
    
    # Load notes configuration using unified system
    from ePy_docs.core.setup import _load_cached_config
    notes_config = _load_cached_config('notes')
    
    if 'layout_styles' not in notes_config:
        raise RuntimeError("Notes configuration missing layout_styles")
    
    layout_styles = notes_config['layout_styles']
    
    if layout_name not in layout_styles:
        raise RuntimeError(f"Layout '{layout_name}' not found in notes configuration")
    
    return layout_styles[layout_name]


class NoteRenderer:
    """Renderer for different types of notes with consistent styling."""
    
    def __init__(self):
        self.note_counter = 0
        self._cross_references = {}
    
    def _get_callout_titles(self, lang: str) -> Dict[str, str]:
        """Get translated callout titles based on language."""
        translations = {
            'en': {
                'note': 'Note',
                'warning': 'Warning',
                'tip': 'Tip',
                'caution': 'Caution',
                'important': 'Important'
            },
            'es': {
                'note': 'Nota',
                'warning': 'Advertencia',
                'tip': 'Consejo',
                'caution': 'Precaución',
                'important': 'Importante'
            }
        }
        
        # No fallback - if language not supported, raise error
        if lang not in translations:
            raise RuntimeError(f"Language '{lang}' not supported. Available: {list(translations.keys())}")
        return translations[lang]
    
    def _load_quarto_config(self) -> Dict[str, Any]:
        """Load quarto configuration from notes.json using unified configuration system."""
        try:
            from ePy_docs.core.setup import _load_cached_config
            return _load_cached_config('notes')
        except Exception as e:
            raise RuntimeError(f"Failed to load notes configuration: {e}")
    
    def _load_color_config(self) -> Dict[str, Any]:
        """Load color configuration from colors.json using unified configuration system."""
        from ePy_docs.core.setup import _load_cached_config
        return _load_cached_config('colors')
    
    def _get_page_language(self) -> str:
        """Get language from report.json configuration."""
        import os
        
        # Get path to report.json from setup.json
        from ePy_docs.core.setup import _load_cached_config
        report_config = _load_cached_config('report')
        
        if 'project' not in report_config:
            raise ValueError("Missing 'project' section in report.json")
        if 'lang' not in report_config['project']:
            raise ValueError("Missing 'lang' in report.json project section")
            
        return report_config['project']['lang']
    
    def _get_note_colors(self, note_type: str) -> Dict[str, Any]:
        """Get color configuration for specific note type."""
        colors_config = self._load_color_config()
        return colors_config['reports']['notes'][note_type]
    
    def _rgb_to_css(self, rgb_list: List[int]) -> str:
        """Convert RGB list to CSS rgb() string."""
        return f"rgb({rgb_list[0]}, {rgb_list[1]}, {rgb_list[2]})"
    
    def _generate_custom_css(self, note_type: str, color_config: Dict[str, Any]) -> str:
        """Generate custom CSS for callout styling with layout-specific styles."""
        # Get layout-specific styling
        layout_style = get_layout_note_style()
        
        # Apply color intensity from layout
        if 'color_intensity' not in layout_style:
            raise RuntimeError("Layout style missing color_intensity")
        color_intensity = layout_style['color_intensity']
        
        # Adjust colors based on intensity
        def adjust_color_intensity(rgb_list: List[int], intensity: float) -> str:
            adjusted = [int(c * intensity + 255 * (1 - intensity)) for c in rgb_list]
            return f"rgb({adjusted[0]}, {adjusted[1]}, {adjusted[2]})"
        
        background = adjust_color_intensity(color_config['background'], color_intensity)
        border = self._rgb_to_css(color_config['border'])
        text_color = self._rgb_to_css(color_config['text_color'])
        icon_color = self._rgb_to_css(color_config['icon_color'])
        
        css_class = f"callout-{note_type}-custom"
        
        # Get layout-specific styling properties - no fallbacks
        required_props = ['font_family', 'font_weight', 'border_radius', 'shadow', 'border_style']
        for prop in required_props:
            if prop not in layout_style:
                raise RuntimeError(f"Layout style missing required property: {prop}")
        
        font_family = layout_style['font_family']
        font_weight = layout_style['font_weight']
        border_radius = layout_style['border_radius']
        shadow = layout_style['shadow']
        border_style = layout_style['border_style']
        
        # Build shadow CSS
        shadow_css = "box-shadow: 0 2px 4px rgba(0,0,0,0.1);" if shadow else ""
        
        return f"""
<style>
.{css_class} {{
    background-color: {background};
    border-left: 4px {border_style} {border};
    border-radius: {border_radius}px;
    padding: 1rem;
    margin: 1rem 0;
    color: {text_color};
    font-family: "{font_family}", sans-serif;
    font-weight: {font_weight};
    {shadow_css}
}}
.{css_class} .callout-title {{
    color: {icon_color};
    font-weight: bold;
    font-family: "{font_family}", sans-serif;
}}
.{css_class} p, .{css_class} li {{
    font-family: "{font_family}", sans-serif;
    font-weight: {font_weight};
}}
</style>
"""
    
    def create_quarto_callout(self, content: str, note_type: str = "note", 
                            title: Optional[str] = None, ref_id: Optional[str] = None,
                            collapse: bool = False, icon: bool = True, 
                            appearance: str = "default") -> Dict[str, str]:
        """Create a Quarto callout block using only JSON configuration with layout-specific styling.
        
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
        
        # Map note_type to quarto callout type
        if note_type not in quarto_config['quarto_callout_types']:
            raise KeyError(f"Note type '{note_type}' not found in quarto_callout_types")
        quarto_type = quarto_config['quarto_callout_types'][note_type]
        
        # Get layout-specific styling
        layout_style = get_layout_note_style()
        
        # Get color configuration from colors.json
        color_config = self._get_note_colors(note_type)
        
        # Apply color intensity from layout style - no fallbacks
        if 'color_intensity' not in layout_style:
            raise RuntimeError("Layout style missing color_intensity")
        color_intensity = layout_style['color_intensity']
        
        # Use only config values - no parameter overrides
        callout_defaults = quarto_config['callout_defaults']
        collapse = callout_defaults['collapse']
        icon = callout_defaults['icon']
        appearance = callout_defaults['appearance']
        
        # Generate reference ID if not provided
        if ref_id is None:
            ref_id = f"{note_type}-{self.note_counter}"
        
        # Generate title if not provided - use automatic translation
        if title is None:
            lang = self._get_page_language()
            callout_titles = self._get_callout_titles(lang)
            title = callout_titles[note_type]  # Don't add counter to title display
        
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
            content,  # Simple content without ContentProcessor 
            note_type
        )
        
        # Generate custom CSS for colors
        custom_css = self._generate_custom_css(note_type, color_config)
        css_class = f"callout-{note_type}-custom"
        
        # Build callout markdown with custom styling
        callout_markdown = custom_css
        callout_markdown += f'::: {{.callout-{quarto_type} .{css_class}{options_str}}}\n'
        
        # Add title - Quarto handles icons automatically based on callout type
        if title:
            callout_markdown += f"## {title}\n"
        
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
        # Get note style from configuration
        notes_config = _load_cached_config('notes')
        return notes_config.get('note_types', {}).get(note_type, {})
    
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
            # Get title from automatic translation
            lang = self._get_page_language()
            callout_titles = self._get_callout_titles(lang)
            type_name = callout_titles[ref_info['type']]
            custom_text = f"{type_name} {ref_info['number']}"
        
        return f"{{{custom_text}}} (@{ref_id})"
    
    def get_cross_references_list(self) -> Dict[str, Dict[str, Any]]:
        """Get a list of all cross-references created.
        
        Returns:
            Dictionary with all cross-references
        """
        return self._cross_references.copy()
