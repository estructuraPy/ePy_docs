"""
Clean note rendering system for ePy_docs.
Generates HTML callouts and Quarto markdown from JSON configuration only.
Following the same pattern as tables.py for layout-specific colors and configuration.
"""

import re
from typing import Dict, Any
from ePy_docs.core.setup import _load_cached_files, _resolve_config_path
from ePy_docs.core.html import MarkdownToHTMLConverter

def _load_notes_config(sync_files: bool = False) -> Dict[str, Any]:
    """Load comprehensive notes configuration from notes.json, colors.json, and text.json.
    Following centralized pattern for unified configuration access.
    
    Args:
        sync_files: Whether to sync configuration files from source
        
    Returns:
        Unified notes configuration dictionary with layout-specific settings
    """
    from ePy_docs.components.pages import get_layout_name
    
    # Load all configuration files with centralized pattern
    notes_config = _load_cached_files(_resolve_config_path('notes', sync_files), sync_files)
    colors_config = _load_cached_files(_resolve_config_path('colors', sync_files), sync_files)
    text_config = _load_cached_files(_resolve_config_path('text', sync_files), sync_files)
    
    # Get current layout
    layout_name = get_layout_name()
    
    # Build unified configuration using unified structure
    unified_config = {}
    
    # 1. Base notes configuration from notes.json
    if 'layout_styles' in notes_config and layout_name in notes_config['layout_styles']:
        layout_notes_config = notes_config['layout_styles'][layout_name]
        unified_config['layout_styles'] = {layout_name: layout_notes_config}
    elif 'layout_styles' in notes_config:
        # Fallback to 'academic' layout if current layout is not found
        fallback_layout = 'academic'
        if fallback_layout in notes_config['layout_styles']:
            layout_notes_config = notes_config['layout_styles'][fallback_layout]
            unified_config['layout_styles'] = {layout_name: layout_notes_config}
        
    # Add other notes config sections
    unified_config['quarto_callout_types'] = notes_config.get('quarto_callout_types', {})
    unified_config['style_mapping'] = notes_config.get('style_mapping', {})
    unified_config['pagebreak_control'] = notes_config.get('pagebreak_control', {})
    
    # 2. Colors from colors.json using NEW unified structure
    if 'layout_styles' in colors_config:
        # Add complete layout_styles from colors.json to unified config
        if 'layout_styles' not in unified_config:
            unified_config['layout_styles'] = {}
        
        # Merge colors layout_styles with notes layout_styles
        if layout_name in colors_config['layout_styles']:
            colors_layout = colors_config['layout_styles'][layout_name]
            if layout_name in unified_config['layout_styles']:
                unified_config['layout_styles'][layout_name].update(colors_layout)
            else:
                unified_config['layout_styles'][layout_name] = colors_layout
        else:
            # Fallback to academic layout from colors
            fallback_layout = 'academic'
            if fallback_layout in colors_config['layout_styles']:
                colors_layout = colors_config['layout_styles'][fallback_layout]
                if layout_name in unified_config['layout_styles']:
                    unified_config['layout_styles'][layout_name].update(colors_layout)
                else:
                    unified_config['layout_styles'][layout_name] = colors_layout
    
    # 3. Typography from text.json for current layout
    if 'layout_styles' in text_config and layout_name in text_config['layout_styles']:
        layout_text = text_config['layout_styles'][layout_name]
        if 'text' in layout_text:
            unified_config['text_config'] = layout_text['text']
    elif 'layout_styles' in text_config:
        # Fallback to 'academic' layout if current layout is not found
        fallback_layout = 'academic'
        if fallback_layout in text_config['layout_styles']:
            layout_text = text_config['layout_styles'][fallback_layout]
            if 'text' in layout_text:
                unified_config['text_config'] = layout_text['text']
    
    return unified_config

class NoteRenderer:
    """Clean callout generator using complete JSON configuration following tables.py pattern."""
    
    def __init__(self, sync_files: bool = False):
        """Initialize renderer with unified configuration loading."""
        self.sync_files = sync_files
        self._config = None
    
    @property
    def config(self) -> Dict[str, Any]:
        """Lazy load unified configuration on first access."""
        if self._config is None:
            self._config = _load_notes_config(sync_files=self.sync_files)
        return self._config
    
    def _get_style_key(self, note_type: str) -> str:
        """Get style key for note type from configuration."""
        config = self.config
        
        # Use mapping if available
        if note_type in config['style_mapping']:
            return config['style_mapping'][note_type]
            
        # Check if direct callout color exists
        if 'callout_colors' in config and note_type in config['callout_colors']:
            return note_type
            
        # Return note_type as-is if no mapping found
        return note_type
    
    def _process_markdown_content(self, content: str) -> str:
        """Process markdown content and convert to HTML using centralized HTML module.
        
        Args:
            content: Raw markdown content
            
        Returns:
            HTML-formatted content for notebook display
        """
        converter = MarkdownToHTMLConverter(sync_files=self.sync_files)
        return converter.convert(content)
    
    def create_note_html(self, content: str, note_type: str, title: str = None) -> str:
        """Create visual HTML callout from JSON configuration using colors.json.
        
        Args:
            content: Text content for the callout
            note_type: Type of note (note, tip, warning, etc.)
            title: Optional title for the callout
            
        Returns:
            HTML string with visual callout styling
        """
        config = self.config
        
        # Get style key
        style_key = self._get_style_key(note_type)
        
        # Get title - use style_key as default if none provided
        if title is None:
            title = style_key.capitalize()
        
        # Get colors from current config - DIRECT ACCESS, NO GUARDIANS
        layout_name = list(config['layout_styles'].keys())[0]  # Get current layout
        layout_config = config['layout_styles'][layout_name]
        
        # Access callouts directly from loaded config
        if 'callouts' in layout_config and style_key in layout_config['callouts']:
            color_info = layout_config['callouts'][style_key]
        else:
            # Fallback to academic layout if current layout doesn't have this callout
            if 'academic' in config['layout_styles'] and 'callouts' in config['layout_styles']['academic']:
                academic_callouts = config['layout_styles']['academic']['callouts']
                color_info = academic_callouts.get(style_key, academic_callouts.get('note', {}))
            else:
                # Ultimate fallback with hardcoded values
                color_info = {
                    'background': [240, 248, 255],
                    'border': [0, 33, 132], 
                    'icon': [0, 33, 132],
                    'text': [0, 0, 0]
                }
        
        # Convert colors to CSS format
        bg_color = f"rgb({color_info['background'][0]}, {color_info['background'][1]}, {color_info['background'][2]})"
        border_color = f"rgb({color_info['border'][0]}, {color_info['border'][1]}, {color_info['border'][2]})"
        # Use icon color for text (standard naming convention)
        text_color = f"rgb({color_info['icon'][0]}, {color_info['icon'][1]}, {color_info['icon'][2]})"
        
        # Get icon from the callout configuration (if available)
        icon = color_info.get('icon_symbol', '💡')  # Default icon if not specified
        
        # Process content
        processed_content = self._process_markdown_content(content)
        
        # Generate HTML with colors from JSON
        html = f"""<div style="
    border: 2px solid {border_color};
    border-left: 6px solid {border_color};
    background-color: {bg_color};
    border-radius: 8px;
    padding: 16px;
    margin: 16px 0;
    font-family: Arial, sans-serif;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
">
    <div style="
        display: flex;
        align-items: center;
        margin-bottom: 12px;
        font-weight: bold;
        color: {border_color};
        font-size: 1.1em;
    ">
        <span style="margin-right: 8px; font-size: 1.2em;">{icon}</span>
        {title}
    </div>
    <div style="
        color: {text_color};
        line-height: 1.5;
    ">
        {processed_content}
    </div>
</div>"""
        
        return html
    
    def create_note_markdown(self, content: str, note_type: str, title: str = None) -> str:
        """Create Quarto callout markdown from JSON configuration.
        
        Args:
            content: Text content for the callout
            note_type: Type of note (note, tip, warning, etc.)
            title: Optional title for the callout
            
        Returns:
            Markdown string with correct Quarto callout syntax
        """
        config = self.config
        
        # Get title - Quarto handles default titles automatically, only use if explicitly provided
        if title is None:
            title = ""  # Empty title lets Quarto use its default localized titles
        
        # Get Quarto type from configuration with correct .callout- prefix
        base_type = config['quarto_callout_types'].get(note_type, 'note')
        quarto_type = f".callout-{base_type}"
        
        # Generate Quarto callout markdown with correct syntax
        markdown = f"::: {{{quarto_type}}}\n"
        if title:  # Only add title if explicitly provided
            markdown += f"## {title}\n\n"
        markdown += f"{content}\n"
        markdown += ":::\n"
        
        return markdown

    def display_callout(self, content: str, note_type: str, title: str = None):
        """Display callout visually in notebook.
        
        Args:
            content: Text content for the callout
            note_type: Type of note (note, tip, warning, etc.)
            title: Optional title for the callout
        """
        html = self.create_note_html(content, note_type, title)
        
        from IPython.display import HTML, display
        display(HTML(html))
