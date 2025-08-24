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
    import os
    from pathlib import Path
    
    # Use package location directly - no fallbacks
    package_path = Path(__file__).parent / "text.json"
    if not package_path.exists():
        raise FileNotFoundError(f"text.json not found in expected location: {package_path}")
    
    try:
        from ePy_docs.api.file_management import read_json
        config = read_json(package_path)
    except Exception as e:
        raise RuntimeError(f"Failed to load text configuration: {e}")
    
    # Validate required configuration exists
    # Note: superscripts, bullet_points, text_enhancement moved to format.json for centralization
    required_keys = ['layout_styles', 'lists', 'validation']
    for key in required_keys:
        if key not in config:
            raise KeyError(f"Required configuration key '{key}' missing in text.json")
    
    return config


def _get_layout_config(layout_name: str) -> dict:
    """Get layout configuration for a specific layout.
    
    Args:
        layout_name: Name of the layout ('academic', 'technical', 'corporate', etc.)
    
    Returns:
        dict: Layout configuration
        
    Raises:
        KeyError: If layout_name not found in configuration
    """
    config = _load_text_config()
    if layout_name not in config['layout_styles']:
        available_layouts = ', '.join(config['layout_styles'].keys())
        raise KeyError(f"Layout '{layout_name}' not found. Available layouts: {available_layouts}")
    return config['layout_styles'][layout_name]


def _get_current_layout_config() -> dict:
    """Get the layout configuration section for the current layout.
    
    Returns:
        Layout configuration dictionary for the current layout
    """
    from ePy_docs.components.page import get_layout_name
    layout_name = get_layout_name()
    layout_config = _get_layout_config(layout_name)
    return layout_config


def format_header_h1(text: str, layout_name: str) -> str:
    """Format H1 header using specified layout.
    
    Args:
        text: Header text
        layout_name: Layout to use ('academic', 'technical', 'corporate', etc.)
        
    Returns:
        Formatted H1 markdown
    """
    layout_config = _get_layout_config(layout_name)
    return layout_config['headers']['h1']['format'].format(text=text)


def format_header_h2(text: str, layout_name: str) -> str:
    """Format H2 header using specified layout.
    
    Args:
        text: Header text
        layout_name: Layout to use ('academic', 'technical', 'corporate', etc.)
        
    Returns:
        Formatted H2 markdown
    """
    layout_config = _get_layout_config(layout_name)
    return layout_config['headers']['h2']['format'].format(text=text)


def format_header_h3(text: str, layout_name: str) -> str:
    """Format H3 header using specified layout.
    
    Args:
        text: Header text
        layout_name: Layout to use ('academic', 'technical', 'corporate', etc.)
        
    Returns:
        Formatted H3 markdown
    """
    layout_config = _get_layout_config(layout_name)
    return layout_config['headers']['h3']['format'].format(text=text)


def format_text_content(content: str) -> str:
    """Format text content.
    
    Args:
        content: Text content to format
        
    Returns:
        Formatted text content
    """
    text_config = _get_current_layout_config()
    return text_config['text']['content_format'].format(content=content)


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
            label: The field label
            value: The field value
            
        Returns:
            Formatted string from configuration
        """
        text_config = _get_current_layout_config()
        return text_config['text']['field_format'].format(label=label, value=value)
    
    @staticmethod
    def format_field_bold(label: str, value: str) -> str:
        """Format a field with bold styling for reports.
        
        Args:
            label: The field label
            value: The field value
            
        Returns:
            Formatted string from configuration
        """
        text_config = _get_current_layout_config()
        return text_config['text']['field_bold_format'].format(label=label, value=value)
    
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
        
        from ePy_docs.core.markdown import MarkdownFormatter
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
        
        # Load superscripts from centralized format.json instead of text.json
        from ePy_docs.components.format import load_format_config
        format_config = load_format_config()
        superscript_config = format_config['superscripts']
        
        def replace_power(match):
            base, power = match.groups()
            if 'character_map' not in superscript_config:
                raise ValueError("Missing 'character_map' in superscript configuration")
            character_map = superscript_config['character_map']
            
            superscript_power = ''.join(
                character_map[char] if char in character_map else char
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
        
        # Load bullet_points from centralized format.json instead of text.json
        from ePy_docs.components.format import load_format_config
        format_config = load_format_config()
        bullet_config = format_config['bullet_points']
        
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
        
        # Load text_enhancement from centralized format.json instead of text.json
        from ePy_docs.components.format import load_format_config
        format_config = load_format_config()
        enhancement_config = format_config['text_enhancement']
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


def apply_text_formatting(text: str, output_format: str = 'matplotlib') -> str:
    """
    Basic text formatting function for compatibility.
    
    Args:
        text: Text to format
        output_format: Output format (default 'matplotlib')
        
    Returns:
        Formatted text with LaTeX math mode when appropriate
    """
    return apply_text_formatting_with_math(text, use_latex_math=True)


def apply_text_formatting_with_math(text: str, use_latex_math: bool = True) -> str:
    """
    Apply text formatting with LaTeX math mode for better font consistency.
    
    Args:
        text: Text to format
        use_latex_math: Whether to use LaTeX math mode for superscripts/subscripts
        
    Returns:
        Formatted text with LaTeX math expressions for superscripts/subscripts
    """
    if not use_latex_math:
        # Import from tables module as fallback
        from ePy_docs.components.tables import apply_text_formatting
        return apply_text_formatting(text)
    
    from ePy_docs.core.setup import _load_cached_config
    
    try:
        # Load format configuration
        format_config = _load_cached_config('units/format', sync_files=True)
        math_config = format_config.get('math_formatting', {})
        
        # Apply superscripts using LaTeX math mode
        if math_config.get('enable_superscript', True):
            superscript_pattern = math_config.get('superscript_pattern', r'\^(\{[^}]+\}|\w)')
            
            def replace_superscript(match):
                content = match.group(1)
                if content.startswith('{') and content.endswith('}'):
                    content = content[1:-1]  # Remove braces
                
                # Use LaTeX math mode for superscripts
                return f"$^{{{content}}}$"
            
            text = re.sub(superscript_pattern, replace_superscript, text)
        
        # Apply subscripts using LaTeX math mode
        if math_config.get('enable_subscript', True):
            subscript_pattern = math_config.get('subscript_pattern', r'_(\{[^}]+\}|\w)')
            
            def replace_subscript(match):
                content = match.group(1)
                if content.startswith('{') and content.endswith('}'):
                    content = content[1:-1]  # Remove braces
                
                # Use LaTeX math mode for subscripts
                return f"$_{{{content}}}$"
            
            text = re.sub(subscript_pattern, replace_subscript, text)
        
        # Apply common Greek letters and symbols
        greek_symbols = {
            'alpha': r'$\alpha$',
            'beta': r'$\beta$', 
            'gamma': r'$\gamma$',
            'delta': r'$\delta$',
            'sigma': r'$\sigma$',
            'tau': r'$\tau$',
            'phi': r'$\phi$',
            'rho': r'$\rho$'
        }
        
        for symbol, latex in greek_symbols.items():
            text = text.replace(symbol, latex)
        
        return text
        
    except Exception as e:
        # Fallback to regular formatting
        return apply_advanced_text_formatting(text, 'matplotlib')


def get_optimal_font_for_mixed_content(text: str) -> str:
    """
    Get optimal font for text that may contain LaTeX math expressions.
    
    Args:
        text: Text that may contain LaTeX math mode expressions
        
    Returns:
        Font family name optimized for mixed text/math content
    """
    # If text contains LaTeX math expressions, use a font that works well with them
    if '$' in text:
        # Computer Modern or Times work well with LaTeX math
        return 'Times New Roman'  # Good compromise for mixed content
    
    # Check for Unicode characters
    has_unicode = any(ord(char) > 127 for char in text)
    
    if has_unicode:
        # For Unicode content, prefer fonts with good coverage but stick to common ones
        return 'Arial'  # Consistent with rest of table
    
    return 'Arial'  # Default consistent font


def apply_mixed_content_formatting(text_obj, formatted_text: str):
    """
    Apply formatting for text that may contain LaTeX math expressions.
    
    Args:
        text_obj: Matplotlib text object
        formatted_text: Text that may contain LaTeX math expressions
    """
    font_family = get_optimal_font_for_mixed_content(formatted_text)
    
    text_obj.set_text(formatted_text)
    text_obj.set_fontfamily(font_family)
    
    # Enable LaTeX rendering if text contains math expressions
    if '$' in formatted_text:
        text_obj.set_usetex(False)  # Use matplotlib's mathtext instead of full LaTeX
        # mathtext uses Computer Modern for math, regular font for text
def get_best_font_for_text(text: str) -> str:
    """
    Determine the best font for displaying text with superscripts/subscripts.
    
    Args:
        text: Text to analyze for Unicode characters
        
    Returns:
        Font family name that best supports the characters in the text
    """
    # Check if text contains Unicode superscript/subscript characters
    unicode_chars = set()
    has_complex_unicode = False
    has_fallback_notation = False
    
    for char in text:
        if ord(char) > 127:  # Non-ASCII characters
            unicode_chars.add(char)
            # Check if it's a complex Unicode character (beyond basic Latin-1)
            if ord(char) > 255:
                has_complex_unicode = True
    
    # Check for fallback notation patterns
    if '^(' in text or '_(' in text or ('^' in text and len(text) > 1) or ('_' in text and has_complex_unicode):
        has_fallback_notation = True
    
    # Decision logic for font selection
    if not unicode_chars and not has_fallback_notation:
        return 'Arial'  # Default for pure ASCII text
    
    # If we have Unicode characters (especially complex ones), prefer DejaVu Sans
    if has_complex_unicode:
        return 'DejaVu Sans'
    
    # For mixed content (some Unicode + fallback notation), use Times New Roman
    # which has decent coverage and better fallback rendering
    if unicode_chars and has_fallback_notation:
        return 'Times New Roman'
    
    # For pure Unicode without fallback, prefer DejaVu Sans
    if unicode_chars and not has_fallback_notation:
        return 'DejaVu Sans'
    
    # For pure fallback notation without Unicode, use Arial
    if has_fallback_notation and not unicode_chars:
        return 'Arial'
    
    # Default fallback
    return 'Arial'


def apply_font_fallback(text_obj, formatted_text: str):
    """
    Apply font with fallback for Unicode characters (matplotlib-specific).
    
    Args:
        text_obj: Matplotlib text object
        formatted_text: Text that may contain Unicode characters
    """
    best_font = get_best_font_for_text(formatted_text)
    text_obj.set_text(formatted_text)
    text_obj.set_fontfamily(best_font)
    
    # Adjust font size based on font choice for optimal readability
    current_size = text_obj.get_fontsize()
    if best_font == 'DejaVu Sans':
        text_obj.set_fontsize(current_size * 0.95)  # Slightly smaller for DejaVu Sans
    elif best_font == 'Times New Roman':
        text_obj.set_fontsize(current_size * 1.0)   # Standard size for Times


def apply_advanced_text_formatting(text: str, output_format: str = 'matplotlib') -> str:
    """Apply advanced text formatting including superscripts and subscripts with fallback support.
    
    Args:
        text: Text to format
        output_format: Output format ('matplotlib', 'unicode', 'html', 'latex', etc.)
        
    Returns:
        Formatted text with proper superscripts, subscripts, and symbols
    """
    try:
        # Load format configuration from centralized format.json
        from ePy_docs.components.format import load_format_config
        format_config = load_format_config()
        
        # Get math formatting configuration
        math_config = format_config.get('math_formatting', {})
        
        # Apply superscripts using regex patterns
        if math_config.get('enable_superscript', True):
            superscript_pattern = math_config.get('superscript_pattern', r'\^(\{[^}]+\}|\w)')
            # Get superscript map from the correct location in format.json
            superscript_map = format_config.get('superscripts', {}).get('character_map', {})
            
            def replace_superscript(match):
                content = match.group(1)
                if content.startswith('{') and content.endswith('}'):
                    content = content[1:-1]  # Remove braces
                
                # Try to convert each character to superscript
                result = ''
                for char in content:
                    unicode_char = superscript_map.get(char, char)
                    # If Unicode conversion didn't change the character, use fallback
                    if unicode_char == char and char not in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
                        # For non-numeric characters that don't have Unicode equivalents,
                        # use parentheses notation as fallback
                        if len(content) == 1:
                            result = f"^{char}"  # Simple superscript notation
                        else:
                            result = f"^({content})"  # Multi-character superscript
                        break
                    else:
                        result += unicode_char
                
                return result
            
            text = re.sub(superscript_pattern, replace_superscript, text)
        
        # Apply subscripts using regex patterns
        if math_config.get('enable_subscript', True):
            subscript_pattern = math_config.get('subscript_pattern', r'_(\{[^}]+\}|\w)')
            # Get subscript map from the correct location in format.json
            subscript_map = format_config.get('subscripts', {}).get('character_map', {})
            
            def replace_subscript(match):
                content = match.group(1)
                if content.startswith('{') and content.endswith('}'):
                    content = content[1:-1]  # Remove braces
                
                # Try to convert each character to subscript
                result = ''
                for char in content:
                    unicode_char = subscript_map.get(char, char)
                    # If Unicode conversion didn't change the character, use fallback
                    if unicode_char == char and char not in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
                        # For non-numeric characters that don't have Unicode equivalents,
                        # use underscore notation as fallback
                        if len(content) == 1:
                            result = f"_{char}"  # Simple subscript notation
                        else:
                            result = f"_({content})"  # Multi-character subscript
                        break
                    else:
                        result += unicode_char
                
                return result
            
            text = re.sub(subscript_pattern, replace_subscript, text)
        
        # Apply format-specific replacements (for units and symbols)
        format_replacements = format_config.get(output_format, {}).get('superscripts', {})
        for pattern, replacement in format_replacements.items():
            text = text.replace(pattern, replacement)
        
        # Apply multiplication operators
        mult_operators = format_config.get('multiplication_operators', {})
        mult_symbol = mult_operators.get(output_format, '·')
        text = text.replace('·', mult_symbol)
        
        return text
        
    except Exception as e:
        # If configuration loading fails, return original text
        print(f"Warning: Could not apply advanced text formatting: {e}")
        return text


