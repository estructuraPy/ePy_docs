"""
Format management for ePy_docs - centralized text formatting configurations.
Provides access to superscripts, bullet points, text enhancements, and display formatting.
"""

import json
import os
from typing import Dict, Any, Optional
from pathlib import Path


def _get_format_config_path() -> Path:
    """Get the path to the format.json configuration file."""
    current_dir = Path(__file__).parent
    return current_dir / "format.json"


def load_format_config() -> Dict[str, Any]:
    """Load the centralized format configuration from format.json."""
    config_path = _get_format_config_path()
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Warning: Could not load format.json: {e}")
        return _get_default_format_config()


def _get_default_format_config() -> Dict[str, Any]:
    """Fallback format configuration if format.json is not available."""
    return {
        "superscripts": {
            "character_map": {
                "0": "⁰", "1": "¹", "2": "²", "3": "³", "4": "⁴",
                "5": "⁵", "6": "⁶", "7": "⁷", "8": "⁸", "9": "⁹",
                "-": "⁻", "+": "⁺"
            },
            "power_pattern": "([a-zA-Z°µ]+)\\^([0-9-]+)"
        },
        "bullet_points": {
            "patterns": ["• ", "* ", "- "],
            "numbered_pattern": "^\\d+\\.\\s+"
        },
        "text_enhancement": {
            "bullet_replacement": "- ",
            "bullet_pattern": "•\\s*",
            "whitespace_cleanup": {
                "multiple_spaces": " +",
                "leading_spaces": "\\n +", 
                "trailing_spaces": " +\\n"
            }
        },
        "display_formatting": {
            "indentation_spaces": 4,
            "max_consecutive_newlines": 2,
            "max_title_width_chars": 80,
            "line_spacing": 0.1,
            "padding": 1
        }
    }


def get_superscript_config() -> Dict[str, Any]:
    """Get superscript configuration."""
    config = load_format_config()
    return config.get('superscripts', {})


def get_bullet_points_config() -> Dict[str, Any]:
    """Get bullet points configuration."""
    config = load_format_config()
    return config.get('bullet_points', {})


def get_text_enhancement_config() -> Dict[str, Any]:
    """Get text enhancement configuration."""
    config = load_format_config()
    return config.get('text_enhancement', {})


def get_unit_display_config() -> Dict[str, Any]:
    """Get unit display configuration including emojis."""
    config = load_format_config()
    return config.get('unit_display', {})


def get_display_formatting_config() -> Dict[str, Any]:
    """Get display formatting configuration."""
    config = load_format_config()
    return config.get('display_formatting', {})


def convert_to_superscript(text: str) -> str:
    """Convert numbers in text to superscript characters."""
    superscript_config = get_superscript_config()
    character_map = superscript_config.get('character_map', {})
    
    result = ""
    for char in text:
        result += character_map.get(char, char)
    return result


def clean_bullet_points(text: str) -> str:
    """Clean and standardize bullet points in text."""
    enhancement_config = get_text_enhancement_config()
    bullet_replacement = enhancement_config.get('bullet_replacement', '- ')
    bullet_pattern = enhancement_config.get('bullet_pattern', '•\\s*')
    
    import re
    return re.sub(bullet_pattern, bullet_replacement, text)


def clean_whitespace(text: str) -> str:
    """Clean excessive whitespace according to configured patterns."""
    enhancement_config = get_text_enhancement_config()
    whitespace_config = enhancement_config.get('whitespace_cleanup', {})
    
    import re
    
    # Clean multiple spaces
    if 'multiple_spaces' in whitespace_config:
        text = re.sub(whitespace_config['multiple_spaces'], ' ', text)
    
    # Clean leading spaces after newlines
    if 'leading_spaces' in whitespace_config:
        text = re.sub(whitespace_config['leading_spaces'], '\n', text)
        
    # Clean trailing spaces before newlines  
    if 'trailing_spaces' in whitespace_config:
        text = re.sub(whitespace_config['trailing_spaces'], '\n', text)
    
    return text


def add_unit_emojis(text: str) -> str:
    """Add emojis to unit descriptions based on configured mappings."""
    unit_config = get_unit_display_config()
    emoji_map = unit_config.get('emojis', {})
    
    for unit_text, emoji_text in emoji_map.items():
        text = text.replace(unit_text, emoji_text)
    
    return text
