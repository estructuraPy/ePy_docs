"""Text formatting utilities for ePy_docs report generation.

Handles specific formatting operations for markdown and text content using
configuration from text.json. All parameters are sourced from JSON configuration
with no hardcoded values or fallbacks.
"""

import os
import json
import re
import tempfile
from typing import Optional, List


def _load_text_config() -> dict:
    """Load text configuration from text.json.
    
    Returns:
        Configuration dictionary from text.json
        
    Raises:
        FileNotFoundError: If text.json is not found
        json.JSONDecodeError: If text.json is invalid
        KeyError: If required configuration is missing
    """
    from ePy_docs.project.setup import get_current_project_config
    
    current_config = get_current_project_config()
    config_path = os.path.join(current_config.folders.config, 'core', 'text.json')
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # Validate required configuration exists
    required_keys = ['headers', 'text', 'lists', 'superscripts', 'bullet_points', 'text_enhancement', 'validation']
    for key in required_keys:
        if key not in config:
            raise KeyError(f"Required configuration key '{key}' missing in text.json")
    
    return config


def format_header_h1(text: str) -> str:
    """Format H1 header.
    
    Args:
        text: Header text
        
    Returns:
        Formatted H1 markdown
        
    Raises:
        FileNotFoundError: If configuration file is missing
        KeyError: If required configuration is missing
        ValueError: If text is empty or too long
    """
    config = _load_text_config()
    
    # Validate input
    if not text:
        raise ValueError("Header text is required")
    
    if len(text) > config['validation']['max_text_length']:
        raise ValueError(f"Header text exceeds maximum length of {config['validation']['max_text_length']}")
    
    return config['headers']['h1']['format'].format(text=text)


def format_header_h2(text: str) -> str:
    """Format H2 header.
    
    Args:
        text: Header text
        
    Returns:
        Formatted H2 markdown
        
    Raises:
        FileNotFoundError: If configuration file is missing
        KeyError: If required configuration is missing
        ValueError: If text is empty or too long
    """
    config = _load_text_config()
    
    # Validate input
    if not text:
        raise ValueError("Header text is required")
    
    if len(text) > config['validation']['max_text_length']:
        raise ValueError(f"Header text exceeds maximum length of {config['validation']['max_text_length']}")
    
    return config['headers']['h2']['format'].format(text=text)


def format_header_h3(text: str) -> str:
    """Format H3 header.
    
    Args:
        text: Header text
        
    Returns:
        Formatted H3 markdown
        
    Raises:
        FileNotFoundError: If configuration file is missing
        KeyError: If required configuration is missing
        ValueError: If text is empty or too long
    """
    config = _load_text_config()
    
    # Validate input
    if not text:
        raise ValueError("Header text is required")
    
    if len(text) > config['validation']['max_text_length']:
        raise ValueError(f"Header text exceeds maximum length of {config['validation']['max_text_length']}")
    
    return config['headers']['h3']['format'].format(text=text)


def format_text_content(content: str) -> str:
    """Format text content.
    
    Args:
        content: Text content to format
        
    Returns:
        Formatted text content
        
    Raises:
        FileNotFoundError: If configuration file is missing
        KeyError: If required configuration is missing
        ValueError: If content is empty or too long
    """
    config = _load_text_config()
    
    # Validate input
    if not content:
        raise ValueError("Text content is required")
    
    if len(content) > config['validation']['max_text_length']:
        raise ValueError(f"Text content exceeds maximum length of {config['validation']['max_text_length']}")
    
    return config['text']['content_format'].format(content=content)


def format_list(items: List[str], ordered: bool = False) -> str:
    """Format list items into markdown list.
    
    Args:
        items: List of items to format
        ordered: Whether to create numbered list
        
    Returns:
        Formatted markdown list
        
    Raises:
        FileNotFoundError: If configuration file is missing
        KeyError: If required configuration is missing
        ValueError: If items list is empty or too long
    """
    config = _load_text_config()
    
    # Validate input
    if not items:
        raise ValueError("List items are required")
    
    if len(items) > config['validation']['max_list_items']:
        raise ValueError(f"List exceeds maximum items of {config['validation']['max_list_items']}")
    
    list_items = []
    if ordered:
        list_config = config['lists']['ordered']
        for i, item in enumerate(items, 1):
            list_items.append(list_config['item_format'].format(number=i, item=item))
    else:
        list_config = config['lists']['unordered']
        for item in items:
            list_items.append(list_config['item_format'].format(item=item))
    
    return "\n".join(list_items) + list_config['spacing']


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
            Formatted string with bold markdown styling from configuration
            
        Raises:
            FileNotFoundError: If configuration file is missing
            KeyError: If required configuration is missing
            ValueError: If label or value is empty
        """
        config = _load_text_config()
        
        # Validate input
        if not label:
            raise ValueError("Field label is required")
        if not value:
            raise ValueError("Field value is required")
        
        return config['text']['field_format'].format(label=label, value=value)
    
    @staticmethod
    def format_field_bold(label: str, value: str) -> str:
        """Format a field with bold styling for reports.
        
        Args:
            label: The field label (e.g., "Project", "Date", "Author")
            value: The field value (e.g., "My Project", "2024-01-01", "John Doe")
            
        Returns:
            Formatted string with bold markdown styling from configuration
            
        Raises:
            FileNotFoundError: If configuration file is missing
            KeyError: If required configuration is missing
            ValueError: If label or value is empty
        """
        config = _load_text_config()
        
        # Validate input
        if not label:
            raise ValueError("Field label is required")
        if not value:
            raise ValueError("Field value is required")
        
        return config['text']['field_bold_format'].format(label=label, value=value)
    
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
        """Converts power notation to unicode superscripts using configuration.
        
        Args:
            text: Text with potential power notation (e.g., m^2)
            
        Returns:
            Text with unicode superscripts replacing power notation
            
        Raises:
            FileNotFoundError: If configuration file is missing
            KeyError: If required configuration is missing
        """
        if not isinstance(text, str):
            return str(text)
        
        config = _load_text_config()
        superscript_config = config['superscripts']
        
        def replace_power(match):
            base, power = match.groups()
            superscript_power = ''.join(
                superscript_config['character_map'].get(char, char) 
                for char in power
            )
            return f"{base}{superscript_power}"
        
        text = re.sub(superscript_config['power_pattern'], replace_power, text)
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
        """Checks if text contains bullet points using configuration patterns.
        
        Args:
            text: Text to check for bullet points.
            
        Returns:
            True if text contains bullet points, False otherwise.
            
        Raises:
            FileNotFoundError: If configuration file is missing
            KeyError: If required configuration is missing
        """
        if not text:
            return False
        
        config = _load_text_config()
        bullet_config = config['bullet_points']
        
        lines = text.split('\n')
        for line in lines:
            stripped = line.strip()
            
            # Check for bullet patterns from config
            for pattern in bullet_config['patterns']:
                if stripped.startswith(pattern):
                    return True
            
            # Check for numbered pattern from config
            if re.match(bullet_config['numbered_pattern'], stripped):
                return True
                
        return False
    
    @staticmethod
    def enhance_table_text_rendering(text: str) -> str:
        """Enhance text rendering for tables using configuration patterns.
        
        Args:
            text: Input text that may contain emojis, symbols, or special formatting
            
        Returns:
            Enhanced text with improved rendering for table display
            
        Raises:
            FileNotFoundError: If configuration file is missing
            KeyError: If required configuration is missing
        """
        if not isinstance(text, str):
            return str(text)
        
        config = _load_text_config()
        enhancement_config = config['text_enhancement']
        whitespace_config = enhancement_config['whitespace_cleanup']
        
        # Preserve and enhance emoji and symbol rendering
        text = TextFormatter.process_superscripts_for_text(text)
        
        # Ensure proper spacing around bullet points using config
        text = re.sub(enhancement_config['bullet_pattern'], 
                     enhancement_config['bullet_replacement'], text)
        
        # Clean up excessive whitespace using config patterns
        text = re.sub(whitespace_config['multiple_spaces'], ' ', text)
        text = re.sub(whitespace_config['leading_spaces'], '\n', text)
        text = re.sub(whitespace_config['trailing_spaces'], '\n', text)
        
        return text.strip()


