"""Note rendering system for reports and presentations.

Provides shared note rendering capabilities including different note types
(note, warning, error, success, tip) with consistent styling and Quarto callout support.
"""

from typing import Optional, Dict, Any, List
import json
import os

from ..core.content import ContentProcessor


class NoteRenderer:
    """Renderer for different types of notes with consistent styling."""
    
    def __init__(self):
        self.note_counter = 0
        self._cross_references = {}
    
    def _load_quarto_config(self) -> Dict[str, Any]:
        """Load quarto configuration from quarto.json"""
        config_path = os.path.join(os.path.dirname(__file__), '..', 'formats', 'quarto.json')
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            # Return default config if file not found
            return {
                'callouts': {
                    'note': {'collapse': False, 'icon': True, 'appearance': 'default'},
                    'warning': {'collapse': False, 'icon': True, 'appearance': 'default'},
                    'tip': {'collapse': False, 'icon': True, 'appearance': 'default'},
                    'caution': {'collapse': False, 'icon': True, 'appearance': 'default'},
                    'important': {'collapse': False, 'icon': True, 'appearance': 'default'}
                }
            }
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in quarto.json: {e}")
    
    def create_quarto_callout(self, content: str, note_type: str = "note", 
                            title: Optional[str] = None, ref_id: Optional[str] = None,
                            collapse: bool = False, icon: bool = True, 
                            appearance: str = "default") -> Dict[str, str]:
        """Create a Quarto callout block.
        
        Args:
            content: Callout content
            note_type: Type of callout (note, warning, caution, important, tip)
            title: Optional title for the callout
            ref_id: Optional reference ID for cross-referencing
            collapse: Whether the callout should be collapsible
            icon: Whether to show the callout icon
            appearance: Callout appearance style
            
        Returns:
            Dictionary with callout markdown and metadata
        """
        self.note_counter += 1
        
        # Load configuration from JSON
        quarto_config = self._load_quarto_config()
        callout_config = quarto_config.get('callouts', {}).get(note_type, {})
        
        # Use config values or passed parameters
        collapse = callout_config.get('collapse', collapse)
        icon = callout_config.get('icon', icon)
        appearance = callout_config.get('appearance', appearance)
        
        # Map to valid Quarto callout types
        quarto_type_map = {
            'note': 'note',
            'warning': 'warning', 
            'caution': 'caution',
            'important': 'important',
            'tip': 'tip',
            'error': 'caution'  # Map error to caution
        }
        
        quarto_type = quarto_type_map.get(note_type, 'note')
        
        # Generate reference ID if not provided
        if ref_id is None:
            ref_id = f"{note_type}-{self.note_counter:03d}"
        
        # Generate title if not provided
        if title is None:
            title_map = {
                'note': 'Nota',
                'warning': 'Advertencia',
                'caution': 'Precaución',
                'important': 'Importante',
                'tip': 'Consejo'
            }
            title = f"{title_map.get(note_type, note_type.title())} {self.note_counter}"
        
        # Build callout options
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
        
        # Apply smart_content transformation to handle multiline strings properly
        smart_content = ContentProcessor.smart_content(content)
        
        # Format content
        formatted_content = self.format_note_content(smart_content, note_type)
        
        # Build callout markdown with correct Quarto format (sin ID personalizado)
        callout_markdown = f"::: {{.callout-{quarto_type}}}\n"
        
        # Add title usando ## en lugar de ###
        callout_markdown += f"## {title}\n"
        
        # Add content - ensure it ends with proper spacing
        if formatted_content.strip():
            # Asegurarnos de que el contenido termina con un salto de línea
            content_with_newline = formatted_content.rstrip() + "\n"
            callout_markdown += content_with_newline
        
        # Close callout - ASEGURANDO que siempre haya una línea en blanco antes del cierre
        # Esto ayuda a que ':::' quede en su propia línea y se renderice correctamente
        callout_markdown += "\n\n:::\n"
        
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
        """Create a cross-reference to a note callout.
        
        Args:
            ref_id: Reference ID of the callout
            custom_text: Optional custom text for the reference
            
        Returns:
            Cross-reference markdown
        """
        if ref_id not in self._cross_references:
            # If reference doesn't exist, create a basic reference
            ref_text = custom_text or f"@{ref_id}"
            return f"{{{ref_text}}}"
        
        ref_info = self._cross_references[ref_id]
        
        if custom_text is None:
            # Generate automatic text based on type and number
            type_names = {
                'note': 'Nota',
                'warning': 'Advertencia',
                'caution': 'Precaución',
                'important': 'Importante',
                'tip': 'Consejo'
            }
            type_name = type_names.get(ref_info['type'], ref_info['type'].title())
            custom_text = f"{type_name} {ref_info['number']}"
        
        # Create cross-reference using Quarto syntax
        return f"{{{custom_text}}} (@{ref_id})"
    
    def get_cross_references_list(self) -> Dict[str, Dict[str, Any]]:
        """Get a list of all cross-references created.
        
        Returns:
            Dictionary with all cross-references
        """
        return self._cross_references.copy()
