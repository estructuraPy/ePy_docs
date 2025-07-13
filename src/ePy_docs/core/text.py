"""Text formatting utilities for ePy_docs report generation.

Handles specific formatting operations for markdown and text content using
the centralized MarkdownFormatter for consistency.
"""

import re
import tempfile
from typing import Optional


class TextFormatter:
    """Formatter class that provides basic utilities for formatting text.
    
    Uses the centralized MarkdownFormatter for consistent markdown processing.
    
    Assumptions:
        Input text follows standard formatting conventions
        Markdown syntax is properly structured in input content
    """
    
    @staticmethod
    def format_field(label: str, value: str) -> str:
        """Format a field with simple styling for reports.
        
        Args:
            label: The field label (e.g., "Project", "Date", "Author")
            value: The field value (e.g., "My Project", "2024-01-01", "John Doe")
            
        Returns:
            Formatted string with simple markdown styling: "**label:** value\n\n"
        
        Example:
            >>> TextFormatter.format_field("Project", "My Project")
            "**Project:** My Project\n\n"
        """
        return f"- *{label}:* {value}\n\n"
    
    @staticmethod
    def format_field_bold(label: str, value: str) -> str:
        """Format a field with bold styling for reports.
        
        Args:
            label: The field label (e.g., "Project", "Date", "Author")
            value: The field value (e.g., "My Project", "2024-01-01", "John Doe")
            
        Returns:
            Formatted string with bold markdown styling: "**label:** value\n\n"
        
        Example:
            >>> TextFormatter.format_field_bold("Project", "My Project")
            "**Project:** My Project\n\n"
        """
        return f"**{label}:** {value}\n\n"
    
    @staticmethod
    def format_markdown_text(text: str) -> str:
        """Enhanced markdown text formatting using centralized MarkdownFormatter.
        
        Args:
            text: Input text to format
            
        Returns:
            Clean, formatted text with proper spacing and enhanced markdown support
        """
        if not text:
            raise ValueError("Text input is required and cannot be empty")
        
        from ePy_docs.formats.markdown import MarkdownFormatter
        return MarkdownFormatter.process_text_content(text)
    
    @staticmethod
    def process_superscripts_for_text(text: str) -> str:
        """Converts power notation to unicode superscripts.
        
        Args:
            text: Text with potential power notation (e.g., m^2)
            
        Returns:
            Text with unicode superscripts replacing power notation
            
        Assumptions:
            Power notation follows the pattern base^exponent
            Unicode superscript characters are supported by the target display system
        """
        if not isinstance(text, str):
            return str(text)
        
        superscript_map = {
            '0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴',
            '5': '⁵', '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹',
            '-': '⁻', '+': '⁺'
        }
        
        def replace_power(match):
            base, power = match.groups()
            superscript_power = ''.join(superscript_map.get(char, char) for char in power)
            return f"{base}{superscript_power}"
        
        text = re.sub(r'([a-zA-Z°µ]+)\^([0-9-]+)', replace_power, text)
        return text
    
    @staticmethod
    def process_superscripts_for_tables(text: str) -> str:
        """Converts power notation to unicode superscripts for table display.
        
        Args:
            text: Text with potential power notation.
            
        Returns:
            Text with unicode superscripts for table formatting.
            
        Assumptions:
            Table display system supports unicode superscript characters.
        """
        return TextFormatter.process_superscripts_for_text(text)
    
    @staticmethod
    def has_bullet_points(text: str) -> bool:
        """Checks if text contains bullet points.
        
        Args:
            text: Text to check for bullet points.
            
        Returns:
            True if text contains bullet points, False otherwise.
            
        Assumptions:
            Recognizes standard bullet point formats (•, *, -, numbered lists).
            Bullet points appear at the beginning of lines after stripping whitespace.
        """
        if not text:
            return False
            
        lines = text.split('\n')
        for line in lines:
            stripped = line.strip()
            if (stripped.startswith('• ') or 
                stripped.startswith('* ') or 
                stripped.startswith('- ') or
                re.match(r'^\d+\.\s+', stripped)):
                return True
                
        return False
    
    @staticmethod
    def enhance_table_text_rendering(text: str) -> str:
        """Enhance text rendering for tables with proper handling of emojis and symbols.
        
        Args:
            text: Input text that may contain emojis, symbols, or special formatting
            
        Returns:
            Enhanced text with improved rendering for table display
        """
        if not isinstance(text, str):
            return str(text)
        
        # Preserve and enhance emoji and symbol rendering
        text = TextFormatter.process_superscripts_for_text(text)
        
        # Ensure proper spacing around bullet points
        text = re.sub(r'•\s*', '• ', text)
        
        # Clean up excessive whitespace while preserving meaningful line breaks
        text = re.sub(r' +', ' ', text)  # Multiple spaces to single space
        text = re.sub(r'\n +', '\n', text)  # Remove leading spaces on new lines
        text = re.sub(r' +\n', '\n', text)  # Remove trailing spaces before newlines
        
        return text.strip()


