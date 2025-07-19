"""Base class for all file writing functionality.

Provides core writing capabilities that are shared across reports, presentations,
and other output formats.
"""

import os
import tempfile
import re
from pathlib import Path
from typing import Dict, List, Any, Optional

import pandas as pd
from pydantic import BaseModel, Field

from ePy_docs.styler.colors import _load_cached_colors


def load_colors():
    """Load colors configuration from colors.json"""
    try:
        return _load_cached_colors()
    except Exception as e:
        # No fallbacks - configuration must be complete
        raise ValueError(f"Failed to load colors configuration: {e}. Please ensure colors.json is properly configured.")


class WriteFiles(BaseModel):
    """Base class for writing files with comprehensive format support."""
    
    file_path: str
    content_buffer: List[str] = Field(default_factory=list)
    auto_print: bool = Field(default=True, description="Whether to print content to console")

    def add_content(self, content: str) -> None:
        """Add content to the buffer with proper markdown spacing.
        
        This method ensures that content is properly spaced for markdown rendering.
        If the content doesn't end with a newline, it adds one to prevent 
        concatenation with the next content block.
        """
        if content:
            # If content doesn't end with newline, add one for proper spacing
            if not content.endswith('\n'):
                content += '\n'
            self.content_buffer.append(content)
    
    def _extract_title_from_content(self) -> Optional[str]:
        """Extract title from the first heading in content.
        
        Returns:
            Title string or None if no heading found
        """
        content = '\n'.join(self.content_buffer)
        
        # Protect callouts from header processing to avoid false positives
        from .content import ContentProcessor
        protected_content, callout_replacements = ContentProcessor.protect_callouts_from_header_processing(content)
        
        lines = protected_content.split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith('# '):
                # Extract title from H1 heading (only from document level, not callouts)
                return line[2:].strip()
        return None

    def generate(self, markdown: bool = False, html: bool = False, pdf: bool = False) -> None:
        """Generate content in the requested formats using Quarto.
        
        Args:
            markdown: Whether to generate markdown output
            html: Whether to generate HTML output
            pdf: Whether to generate PDF output
        """
        # Ensure at least one format is requested
        if not any([markdown, html, pdf]):
            raise ValueError("No output formats requested. At least one format (markdown, html, or pdf) must be selected.")
            
        # Create the directory if needed
        directory = os.path.dirname(self.file_path)
        if directory:
            os.makedirs(directory, exist_ok=True)
            
        # Base filename without extension
        base_filename = os.path.splitext(self.file_path)[0]
        
        # Write markdown content if requested or needed for other formats
        markdown_path = f"{base_filename}.md"
        with open(markdown_path, 'w', encoding='utf-8') as f:
            # Join content buffer preserving all user-defined formatting
            content = '\n'.join(self.content_buffer)
            # Ensure content ends with a newline if it doesn't already
            if content and not content.endswith('\n'):
                content += '\n'
            f.write(content)
        
        # Use Quarto for HTML and PDF generation
        if html or pdf:
            from ePy_docs.formats.quarto import QuartoConverter
            
            # Extract title from first heading or use filename
            title = self._extract_title_from_content()
            if not title:
                raise ValueError("No title found in content. Please add an H1 heading (# Title) to your content.")
            
            from ePy_docs.files.data import _load_cached_json
            config = _load_cached_json("quarto_defaults.json")
            if not config or "author" not in config:
                raise ValueError("quarto_defaults.json not found or missing 'author' field")
            
            author = config["author"]
            
            converter = QuartoConverter()
            
            # Generate HTML if requested
            if html:
                converter.convert_markdown_to_html(
                    markdown_content=markdown_path,
                    title=title,
                    author=author,
                    output_file=f"{base_filename}.html"
                )
            
            # Generate PDF if requested
            if pdf:
                converter.convert_markdown_to_pdf(
                    markdown_content=markdown_path,
                    title=title,
                    author=author,
                    output_file=f"{base_filename}.pdf"
                )
        
        # Remove temporary markdown file if it wasn't requested
        if not markdown and os.path.exists(markdown_path):
            os.remove(markdown_path)

    def save(self) -> str:
        """Save content to markdown file.
        
        Returns:
            Path to the saved file
        """
        # Create the directory if needed
        directory = os.path.dirname(self.file_path)
        if directory:
            os.makedirs(directory, exist_ok=True)
        
        # Write content to file
        with open(self.file_path, 'w', encoding='utf-8') as f:
            content = ''.join(self.content_buffer)
            if content and not content.endswith('\n'):
                content += '\n'
            f.write(content)
        
        return self.file_path

    def _create_note_dataframe(self, processed_content: str) -> Optional[pd.DataFrame]:
        """Create a DataFrame from note content for image generation.
        
        Args:
            processed_content: HTML content containing note information
            
        Returns:
            DataFrame suitable for table image generation or None if parsing fails
        """
        try:
            import pandas as pd
            import re
            
            # Extract note content and type
            note_match = re.search(r'<div class="note-(\w+)"><b>(\w+):</b>\s*(.*?)</div>', processed_content)
            if note_match:
                note_type, note_label, note_text = note_match.groups()
                
                # Clean HTML tags from note text
                clean_text = re.sub(r'<[^>]+>', '', note_text).strip()
                
                # Create a simple DataFrame for the note
                note_df = pd.DataFrame({
                    'Tipo': [note_label],
                    'Contenido': [clean_text]
                })
                
                return note_df
            else:
                # Try to extract any content from the note div
                div_match = re.search(r'<div[^>]*>(.*?)</div>', processed_content, re.DOTALL)
                if div_match:
                    content = re.sub(r'<[^>]+>', '', div_match.group(1)).strip()
                    if content:
                        note_df = pd.DataFrame({
                            'Nota': [content]
                        })
                        return note_df
                        
        except Exception:
            # Si hay error devolver None, el método que llama manejará el caso
            return None

    # Basic header methods that can be overridden by subclasses
    def add_h1(self, text: str, color: Optional[str] = None) -> None:
        """Add an H1 header."""
        self.add_content(f"\n# {text}\n\n")

    def add_h2(self, text: str, color: Optional[str] = None) -> None:
        """Add an H2 header."""
        self.add_content(f"\n## {text}\n\n")

    def add_h3(self, text: str, add_newline: bool = True, color: Optional[str] = None) -> None:
        """Add an H3 header."""
        content = f"\n### {text}\n"
        if add_newline:
            content += "\n"
        self.add_content(content)
