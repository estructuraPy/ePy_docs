"""Note rendering system for reports and presentations.

Provides shared note rende        # Build callout markdown with correct Quarto format
        callout_markdown = f":::\u007b.callout-{quarto_type}"ng capabilities including different note types
(note, warning, error, success, tip) with consistent styling and Quarto callout support.
"""

from typing import Optional, Dict, Any, List
import pandas as pd
import os

from ..core.content import ContentProcessor
from .images import ImageProcessor


class NoteRenderer:
    """Renderer for different types of notes with consistent styling."""
    
    def __init__(self):
        self.note_counter = 0
        self.image_processor = ImageProcessor()
        self._cross_references = {}
    
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
        
        # Format content
        formatted_content = self.format_note_content(content, note_type)
        
        # Build callout markdown with correct Quarto format
        callout_markdown = f"::: {{.callout-{note_type}"
        
        # Add options if any
        if options_str:
            callout_markdown += options_str
        
        callout_markdown += f"}}\n"
        
        # Add title
        callout_markdown += f"## {title}\n\n"
        
        # Add content
        callout_markdown += f"{formatted_content}\n"
        
        # Close callout
        callout_markdown += ":::"
        
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
    
    def create_note_dataframe(self, content: str, note_type: str = "note", 
                            title: Optional[str] = None) -> Optional[pd.DataFrame]:
        """Create a DataFrame for note rendering.
        
        Args:
            content: Note content
            note_type: Type of note (note, warning, error, success, tip)
            title: Optional title for the note
            
        Returns:
            DataFrame suitable for image generation
        """
        try:
            # Create a simple DataFrame for the note
            if title:
                note_df = pd.DataFrame({
                    'Tipo': [title],
                    'Contenido': [content]
                })
            else:
                note_df = pd.DataFrame({
                    'Nota': [content]
                })
            
            return note_df
        except Exception:
            return None
    
    def create_multiple_note_images(self, content: str, note_type: str = "note", 
                                  title: str = "Nota", output_dir: str = ".", 
                                  note_number: int = 1, max_lines_per_note: Optional[int] = None) -> List[str]:
        """Create multiple note images if content is too long.
        
        Args:
            content: Note content
            note_type: Type of note
            title: Note title
            output_dir: Directory to save images
            note_number: Sequential note number
            max_lines_per_note: Maximum lines per note image
            
        Returns:
            List of paths to generated note images
        """
        try:
            # Split content into manageable chunks if needed
            max_lines = max_lines_per_note or 15  # Default max lines
            content_lines = content.split('\n')
            
            if len(content_lines) <= max_lines:
                # Single note image
                note_df = self.create_note_dataframe(content, note_type, title)
                if note_df is None:
                    return []
                
                note_path = os.path.join(output_dir, f"note_{note_number:03d}.png")
                success = self.image_processor.create_table_image(
                    note_df, 
                    note_path,
                    note_type=note_type
                )
                return [note_path] if success else []
            else:
                # Multiple note images
                note_paths = []
                chunk_size = max_lines
                chunks = [content_lines[i:i + chunk_size] for i in range(0, len(content_lines), chunk_size)]
                
                for i, chunk in enumerate(chunks):
                    chunk_content = '\n'.join(chunk)
                    chunk_title = f"{title} (Parte {i+1}/{len(chunks)})"
                    
                    note_df = self.create_note_dataframe(chunk_content, note_type, chunk_title)
                    if note_df is not None:
                        note_path = os.path.join(output_dir, f"note_{note_number:03d}_{i+1:02d}.png")
                        success = self.image_processor.create_table_image(
                            note_df, 
                            note_path,
                            note_type=note_type
                        )
                        if success:
                            note_paths.append(note_path)
                
                return note_paths
                
        except Exception:
            return []
    
    def format_note_content(self, content: str, note_type: str = "note") -> str:
        """Format note content for display.
        
        Args:
            content: Raw note content
            note_type: Type of note
            
        Returns:
            Formatted content
        """
        return ContentProcessor.smart_content_formatter(content)
    
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
            ref_text = custom_text or f"ver @{ref_id}"
            return f"({ref_text})"
        
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
        return f"({custom_text}: @{ref_id})"
    
    def get_cross_references_list(self) -> Dict[str, Dict[str, Any]]:
        """Get a list of all cross-references created.
        
        Returns:
            Dictionary with all cross-references
        """
        return self._cross_references.copy()


# Convenience functions for direct use
def create_note_callout(content: str, note_type: str = "note", title: str = None, 
                       ref_id: str = None, renderer: NoteRenderer = None) -> str:
    """Create a Quarto note callout.
    
    Args:
        content: Note content
        note_type: Type of note
        title: Optional title
        ref_id: Optional reference ID
        renderer: Optional renderer instance
        
    Returns:
        Complete markdown string for the callout
    """
    if renderer is None:
        renderer = NoteRenderer()
    
    callout = renderer.create_quarto_callout(content, note_type, title, ref_id)
    return f"\n\n{callout['markdown']}\n\n"


def create_warning_callout(content: str, title: str = None, ref_id: str = None, 
                          renderer: NoteRenderer = None) -> str:
    """Create a warning callout."""
    return create_note_callout(content, "warning", title, ref_id, renderer)


def create_tip_callout(content: str, title: str = None, ref_id: str = None, 
                      renderer: NoteRenderer = None) -> str:
    """Create a tip callout."""
    return create_note_callout(content, "tip", title, ref_id, renderer)


def create_important_callout(content: str, title: str = None, ref_id: str = None, 
                           renderer: NoteRenderer = None) -> str:
    """Create an important callout."""
    return create_note_callout(content, "important", title, ref_id, renderer)
