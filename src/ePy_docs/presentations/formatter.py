"""Presentation formatter for ePy_docs - Specialized for slide-based content.

Provides presentation-specific functionality including slide management,
transitions, themes, and optimized layouts for presentation formats.
"""

import os
import tempfile
from typing import Dict, List, Any, Optional, Union
from enum import Enum
from pydantic import Field

from ..core.base import WriteFiles
from ..core.content import ContentProcessor
from ..core.text import TextFormatter
from ..components.tables import create_table_image
from ..components.images import ImageProcessor
from ..components.notes import NoteRenderer


class PresentationFormat(Enum):
    """Supported presentation formats."""
    REVEAL_JS = "revealjs"
    BEAMER = "beamer"
    POWERPOINT = "pptx"


class PresentationFormatter(WriteFiles):
    """Formatter specifically designed for presentations."""
    
    # Pydantic fields for presentation-specific attributes
    presentation_format: PresentationFormat = Field(default=PresentationFormat.REVEAL_JS, description="Presentation format")
    theme: str = Field(default="default", description="Presentation theme")
    slide_counter: int = Field(default=0, description="Counter for slide numbering")
    current_slide_content: List[str] = Field(default_factory=list, description="Content for current slide")
    output_dir: str = Field(default="", description="Output directory for generated files")
    
    model_config = {"arbitrary_types_allowed": True}
    
    def __init__(self, **data):
        # Extract presentation-specific parameters before calling super().__init__
        presentation_format = data.pop('presentation_format', PresentationFormat.REVEAL_JS)
        theme = data.pop('theme', 'default')
        
        super().__init__(**data)
        
        # Set the extracted values
        self.presentation_format = presentation_format
        self.theme = theme
        
        # Setup output directory
        if not self.output_dir:
            self.output_dir = os.path.dirname(self.file_path)
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Initialize with presentation metadata
        self._add_presentation_metadata()
    
    def _add_presentation_metadata(self):
        """Add presentation-specific metadata to the beginning."""
        metadata = f"""---
title: "Presentation"
format: 
  {self.presentation_format.value}:
    theme: {self.theme}
    transition: slide
    background-transition: fade
    highlight-style: github
---

"""
        self.add_content(metadata)
    
    def add_title_slide(self, title: str, subtitle: str = None, author: str = None, 
                       date: str = None, institution: str = None):
        """Add title slide to presentation."""
        self.slide_counter += 1
        
        slide_content = f"\n# {title}\n\n"
        
        if subtitle:
            slide_content += f"## {subtitle}\n\n"
        
        if author:
            slide_content += f"**{author}**\n\n"
        
        if institution:
            slide_content += f"*{institution}*\n\n"
        
        if date:
            slide_content += f"{date}\n\n"
        
        self.add_content(slide_content)
        self.add_slide_break()
    
    def add_section_slide(self, section_title: str, subtitle: str = None):
        """Add section slide to break up presentation."""
        self.slide_counter += 1
        
        slide_content = f"\n# {section_title}\n\n"
        
        if subtitle:
            slide_content += f"## {subtitle}\n\n"
        
        self.add_content(slide_content)
        self.add_slide_break()
    
    def add_content_slide(self, title: str, content: str = None, 
                         bullet_points: List[str] = None,
                         image_path: str = None, table_df = None):
        """Add content slide with various content types."""
        self.slide_counter += 1
        
        slide_content = f"\n## {title}\n\n"
        
        if content:
            slide_content += f"{content}\n\n"
        
        if bullet_points:
            for point in bullet_points:
                slide_content += f"- {point}\n"
            slide_content += "\n"
        
        if image_path:
            # Process image for presentation
            organized_path = ImageProcessor.organize_image(image_path, self.output_dir, "figures")
            rel_path = ImageProcessor.get_relative_path(organized_path, self.output_dir)
            slide_content += f"![Image]({rel_path})\n\n"
        
        if table_df is not None:
            # Create table image optimized for presentations
            tables_dir = os.path.join(self.output_dir, "tables")
            os.makedirs(tables_dir, exist_ok=True)
            
            img_path = create_table_image(
                df=table_df, output_dir=tables_dir, 
                table_number=self.slide_counter, title="",
                dpi=150  # Lower DPI for presentations
            )
            
            rel_path = ImageProcessor.get_relative_path(img_path, self.output_dir)
            slide_content += f"![Table]({rel_path})\n\n"
        
        self.add_content(slide_content)
        self.add_slide_break()
    
    def add_two_column_slide(self, title: str, left_content: str, right_content: str):
        """Add slide with two-column layout."""
        self.slide_counter += 1
        
        slide_content = f"\n## {title}\n\n"
        slide_content += ":::: {.columns}\n\n"
        slide_content += "::: {.column width=\"50%\"}\n"
        slide_content += f"{left_content}\n"
        slide_content += ":::\n\n"
        slide_content += "::: {.column width=\"50%\"}\n"
        slide_content += f"{right_content}\n"
        slide_content += ":::\n\n"
        slide_content += "::::\n\n"
        
        self.add_content(slide_content)
        self.add_slide_break()
    
    def add_image_slide(self, title: str, image_path: str, caption: str = None):
        """Add slide focused on an image."""
        self.slide_counter += 1
        
        organized_path = ImageProcessor.organize_image(image_path, self.output_dir, "figures")
        rel_path = ImageProcessor.get_relative_path(organized_path, self.output_dir)
        
        slide_content = f"\n## {title}\n\n"
        slide_content += f"![{caption or 'Image'}]({rel_path})\n\n"
        
        if caption:
            slide_content += f"*{caption}*\n\n"
        
        self.add_content(slide_content)
        self.add_slide_break()
    
    def add_slide_break(self):
        """Add slide break for presentation formats."""
        if self.presentation_format == PresentationFormat.REVEAL_JS:
            self.add_content("\n---\n\n")
        elif self.presentation_format == PresentationFormat.BEAMER:
            self.add_content("\n\\framebreak\n\n")
        else:
            self.add_content("\n\n")
    
    def add_speaker_notes(self, notes: str):
        """Add speaker notes to current slide."""
        if self.presentation_format == PresentationFormat.REVEAL_JS:
            notes_content = f"\n::: {{.notes}}\n{notes}\n:::\n\n"
            self.add_content(notes_content)
    
    def add_transition(self, transition_type: str = "slide"):
        """Add custom transition to next slide."""
        if self.presentation_format == PresentationFormat.REVEAL_JS:
            self.add_content(f"\n<!-- .slide: data-transition=\"{transition_type}\" -->\n\n")
    
    def add_background_image(self, image_path: str):
        """Add background image to slide."""
        if self.presentation_format == PresentationFormat.REVEAL_JS:
            organized_path = ImageProcessor.organize_image(image_path, self.output_dir, "backgrounds")
            rel_path = ImageProcessor.get_relative_path(organized_path, self.output_dir)
            self.add_content(f"\n<!-- .slide: data-background=\"{rel_path}\" -->\n\n")
    
    def generate_presentation(self, output_format: str = None) -> str:
        """Generate presentation in specified format."""
        if output_format is None:
            output_format = self.presentation_format.value
        
        # Process content
        content = ''.join(self.content_buffer)
        processed_content = ContentProcessor.format_content(content)
        
        # Write to file
        base_filename = os.path.splitext(self.file_path)[0]
        
        if output_format == "revealjs":
            output_file = f"{base_filename}.html"
        elif output_format == "beamer":
            output_file = f"{base_filename}.pdf"
        elif output_format == "pptx":
            output_file = f"{base_filename}.pptx"
        else:
            output_file = f"{base_filename}.{output_format}"
        
        # Save markdown first
        markdown_path = f"{base_filename}.qmd"
        with open(markdown_path, 'w', encoding='utf-8') as f:
            f.write(processed_content)
        
        # Convert using Quarto
        try:
            from ePy_docs.formats.quarto import QuartoConverter
            converter = QuartoConverter()
            
            if output_format == "revealjs":
                converter.convert_to_revealjs(markdown_path, output_file)
            elif output_format == "beamer":
                converter.convert_to_beamer(markdown_path, output_file)
            elif output_format == "pptx":
                converter.convert_to_powerpoint(markdown_path, output_file)
            
        except ImportError:
            # Fallback: just save the markdown/qmd file
            print(f"Quarto converter not available. Saved presentation as {markdown_path}")
        
        return output_file
    
    def get_slide_count(self) -> int:
        """Get current number of slides."""
        return self.slide_counter
