"""Mathematical and formatting utilities for ePy_docs.

Unified module for equation processing, mathematical formatting, superscripts, subscripts,
and special text formatting. Consolidates functionality from equations.py and format.py.
"""

import re
import json
from typing import List, Optional, Dict, Any, Union
from pathlib import Path
from pydantic import BaseModel, Field

class MathProcessor(BaseModel):
    """Unified processor for mathematical content and formatting."""
    
    equation_counter: int = Field(default=0, description="Counter for equation numbering")
    config: Optional[Dict[str, Any]] = Field(default=None, description="Math configuration")
    
    def __init__(self, **data):
        super().__init__(**data)
        if self.config is None:
            self.config = load_math_config()
    
    def increment_counter(self) -> int:
        """Increment and return the equation counter."""
        self.equation_counter += 1
        return self.equation_counter
    
    def format_equation(self, latex_code: str, label: str = None, caption: str = None) -> Dict[str, str]:
        """Format a single equation for Quarto rendering.
        
        Args:
            latex_code: Raw LaTeX equation code (can be multiline, preserves format)
            label: Optional label for cross-referencing
            caption: Optional caption for the equation
            
        Returns:
            Dictionary with formatted equation parts
        """
        # Clean and normalize the LaTeX code, but preserve multiline format
        clean_latex = self._clean_latex_code(latex_code)
        
        # Generate label automatically only if user didn't provide one
        if label is None:
            label = f"eq-{self.increment_counter()}"
        
        # Check if already properly formatted (single line with label)
        if (clean_latex.startswith('$$') and 
            clean_latex.endswith(f'$$ {{#{label}}}') and
            '\n' not in clean_latex):
            # Already in single line format - preserve as is
            equation_text = clean_latex
        else:
            # Format for Quarto - use compact multiline format that works
            if clean_latex.startswith('$$') and clean_latex.endswith('$$'):
                # Extract content between $$
                content = clean_latex[2:-2].strip()
                # Format as multiline for better readability while maintaining Quarto compatibility
                equation_text = f"$$\n{content}\n$$ {{#{label}}}"
            else:
                # Add $$ delimiters if not present
                equation_text = f"$$\n{clean_latex}\n$$ {{#{label}}}"
        
        result = {
            'equation_text': equation_text,
            'label': label,
            'counter': self.equation_counter
        }
        
        if caption:
            result['caption'] = caption
            
        return result
    
    def _clean_latex_code(self, latex_code: str) -> str:
        """Clean and normalize LaTeX code while preserving essential formatting."""
        if not latex_code:
            return ""
        
        # Remove leading/trailing whitespace but preserve internal structure
        cleaned = latex_code.strip()
        
        # Normalize line breaks - preserve intentional breaks but clean up excess
        cleaned = re.sub(r'\n\s*\n\s*\n+', '\n\n', cleaned)  # Max 2 consecutive newlines
        cleaned = re.sub(r'[ \t]+', ' ', cleaned)  # Normalize spaces
        
        return cleaned
    
    def format_superscript(self, text: str) -> str:
        """Convert text with superscript notation to Unicode superscripts.
        
        Args:
            text: Text containing superscript patterns like x^2 or x^{2n+1}
            
        Returns:
            Text with Unicode superscript characters
        """
        if not self.config['superscripts']['enable_superscript']:
            return text
        
        char_map = self.config['superscripts']['character_map']
        pattern = self.config['superscripts']['superscript_pattern']
        
        def replace_superscript(match):
            content = match.group(1)
            # Remove braces if present
            if content.startswith('{') and content.endswith('}'):
                content = content[1:-1]
            
            # Convert each character to superscript
            result = ''
            for char in content:
                if char in char_map:
                    result += char_map[char]
                else:
                    result += char  # Keep original if no mapping exists
            return result
        
        return re.sub(pattern, replace_superscript, text)
    
    def format_subscript(self, text: str) -> str:
        """Convert text with subscript notation to Unicode subscripts.
        
        Args:
            text: Text containing subscript patterns like H_2O or x_{i,j}
            
        Returns:
            Text with Unicode subscript characters
        """
        if not self.config['subscripts']['enable_subscript']:
            return text
        
        char_map = self.config['subscripts']['character_map']
        pattern = self.config['subscripts']['subscript_pattern']
        
        def replace_subscript(match):
            content = match.group(1)
            # Remove braces if present
            if content.startswith('{') and content.endswith('}'):
                content = content[1:-1]
            
            # Convert each character to subscript
            result = ''
            for char in content:
                if char in char_map:
                    result += char_map[char]
                else:
                    result += char  # Keep original if no mapping exists
            return result
        
        return re.sub(pattern, replace_subscript, text)
    
    def format_math_text(self, text: str) -> str:
        """Apply comprehensive mathematical formatting to text.
        
        Args:
            text: Text to format with mathematical notation
            
        Returns:
            Text with applied mathematical formatting
        """
        formatted_text = text
        
        # Apply superscript formatting
        formatted_text = self.format_superscript(formatted_text)
        
        # Apply subscript formatting
        formatted_text = self.format_subscript(formatted_text)
        
        # Apply unit pattern replacements
        unit_patterns = self.config['math_formatting']['unit_patterns']
        for category, patterns in unit_patterns.items():
            for pattern, replacement in patterns.items():
                formatted_text = formatted_text.replace(pattern, replacement)
        
        return formatted_text
    
    def enhance_text_formatting(self, text: str) -> str:
        """Apply text enhancement formatting including bullet points and whitespace cleanup.
        
        Args:
            text: Text to enhance
            
        Returns:
            Enhanced text with improved formatting
        """
        enhanced_text = text
        
        # Clean up bullet points
        bullet_pattern = self.config['text_enhancement']['bullet_pattern']
        bullet_replacement = self.config['text_enhancement']['bullet_replacement']
        enhanced_text = re.sub(bullet_pattern, bullet_replacement, enhanced_text)
        
        # Apply whitespace cleanup
        cleanup_rules = self.config['text_enhancement']['whitespace_cleanup']
        for rule_name, pattern in cleanup_rules.items():
            if rule_name == 'multiple_spaces':
                enhanced_text = re.sub(pattern, ' ', enhanced_text)
            elif rule_name == 'leading_spaces':
                enhanced_text = re.sub(pattern, '\\n', enhanced_text)
            elif rule_name == 'trailing_spaces':
                enhanced_text = re.sub(pattern, '\\n', enhanced_text)
            elif rule_name == 'empty_lines':
                enhanced_text = re.sub(pattern, '\\n\\n', enhanced_text)
        
        return enhanced_text
    
    def insert_mathematical_symbol(self, text: str, symbol_name: str) -> str:
        """Insert mathematical symbols by name.
        
        Args:
            text: Text where to insert symbol
            symbol_name: Name of the symbol (e.g., 'plus_minus', 'integral')
            
        Returns:
            Text with symbol inserted, or original text if symbol not found
        """
        symbols = self.config['mathematical_symbols']
        
        # Search in all symbol categories
        for category, symbol_dict in symbols.items():
            if symbol_name in symbol_dict:
                return symbol_dict[symbol_name]
        
        # If not found, return original text
        print(f"Warning: Mathematical symbol '{symbol_name}' not found")
        return text
    
    def get_special_character(self, char_name: str) -> str:
        """Get special character by name.
        
        Args:
            char_name: Name of the special character (e.g., 'degree', 'mu', 'alpha')
            
        Returns:
            Special character or original name if not found
        """
        special_chars = self.config['display_formatting']['special_characters']
        
        if char_name in special_chars:
            return special_chars[char_name]
        
        print(f"Warning: Special character '{char_name}' not found")
        return char_name
    
    def format_emphasis(self, text: str, emphasis_type: str) -> str:
        """Apply emphasis formatting (bold, italic, code).
        
        Args:
            text: Text to format
            emphasis_type: Type of emphasis ('bold', 'italic', 'code')
            
        Returns:
            Formatted text with emphasis applied
        """
        emphasis_formats = self.config['display_formatting']['emphasis']
        
        if emphasis_type in emphasis_formats:
            format_template = emphasis_formats[emphasis_type]
            return format_template.format(text=text)
        
        print(f"Warning: Emphasis type '{emphasis_type}' not found")
        return text
    
    def process_equations_in_text(self, text: str, auto_number: bool = True) -> str:
        """Process and format all equations found in text.
        
        Args:
            text: Text containing equations
            auto_number: Whether to automatically number equations
            
        Returns:
            Text with processed and formatted equations
        """
        # Pattern to find equation blocks
        equation_pattern = r'\$\$(.*?)\$\$'
        
        def replace_equation(match):
            equation_content = match.group(1).strip()
            if auto_number:
                formatted_eq = self.format_equation(equation_content)
                return formatted_eq['equation_text']
            else:
                return f"$${equation_content}$$"
        
        return re.sub(equation_pattern, replace_equation, text, flags=re.DOTALL)

def load_math_config(sync_files: bool = False) -> Dict[str, Any]:
    """Load mathematical configuration from math.json using centralized caching.
    
    Args:
        sync_files: Whether to sync configuration files
        
    Returns:
        Mathematical configuration dictionary from math.json
    """
    try:
        from ePy_docs.core.setup import _load_cached_files, _resolve_config_path
        config_path = _resolve_config_path('math', sync_files=sync_files)
        return _load_cached_files(config_path, sync_files=sync_files)
    except (ImportError, FileNotFoundError) as e:
        print(f"Warning: Could not load math.json using centralized system: {e}")
        return _load_math_config_direct()

def _load_math_config_direct() -> Dict[str, Any]:
    """Direct loading of math.json configuration."""
    config_path = Path(__file__).parent / "math.json"
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Warning: Could not load math.json: {e}")
        return _get_default_math_config()

def _get_default_math_config() -> Dict[str, Any]:
    """Minimal fallback configuration - real config should come from math.json."""
    return {
        "equations": {
            "formatting": {
                "inline_delimiter": "$",
                "block_delimiter": "$$",
                "numbering": True
            }
        },
        "superscripts": {"enable_superscript": True},
        "subscripts": {"enable_subscript": True},
        "math_formatting": {
            "enable_superscript": True,
            "enable_subscript": True,
            "unit_patterns": {}
        },
        "text_enhancement": {
            "bullet_replacement": "- ",
            "bullet_pattern": "•\\s*"
        },
        "display_formatting": {
            "emphasis": {
                "bold": "**{text}**",
                "italic": "*{text}*",
                "code": "`{text}`"
            },
            "special_characters": {"degree": "°"}
        },
        "mathematical_symbols": {
            "operators": {"plus_minus": "±"}
        }
    }

# Convenience functions for common operations
def format_superscript(text: str, sync_files: bool = False) -> str:
    """Convenience function to format superscripts."""
    processor = MathProcessor(config=load_math_config(sync_files=sync_files))
    return processor.format_superscript(text)

def format_subscript(text: str, sync_files: bool = False) -> str:
    """Convenience function to format subscripts."""
    processor = MathProcessor(config=load_math_config(sync_files=sync_files))
    return processor.format_subscript(text)

def format_equation(latex_code: str, label: str = None, caption: str = None, sync_files: bool = False) -> Dict[str, str]:
    """Convenience function to format equations."""
    processor = MathProcessor(config=load_math_config(sync_files=sync_files))
    return processor.format_equation(latex_code, label, caption)

def format_math_text(text: str, sync_files: bool = False) -> str:
    """Convenience function for comprehensive mathematical text formatting."""
    processor = MathProcessor(config=load_math_config(sync_files=sync_files))
    return processor.format_math_text(text)

def get_mathematical_symbol(symbol_name: str, sync_files: bool = False) -> str:
    """Convenience function to get mathematical symbols."""
    processor = MathProcessor(config=load_math_config(sync_files=sync_files))
    return processor.insert_mathematical_symbol("", symbol_name)

def get_special_character(char_name: str, sync_files: bool = False) -> str:
    """Convenience function to get special characters."""
    processor = MathProcessor(config=load_math_config(sync_files=sync_files))
    return processor.get_special_character(char_name)
