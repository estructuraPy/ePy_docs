"""Note rendering system for reports and presentations.

Provides shared note rendering capabilities including different note types
(note, warning, error, success, tip) with consistent styling.
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
