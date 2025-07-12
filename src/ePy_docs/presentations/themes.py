"""Themes and styling for presentations.

Provides predefined themes and styling options for different types
of presentations including corporate, academic, and minimal themes.
"""

from enum import Enum
from typing import Dict, Any


class ThemeType(Enum):
    """Available presentation themes."""
    DEFAULT = "default"
    CORPORATE = "corporate"
    ACADEMIC = "academic"
    MINIMAL = "minimal"
    DARK = "dark"
    ELEGANT = "elegant"


class PresentationTheme:
    """Manager for presentation themes and styling."""
    
    def __init__(self, theme_type: ThemeType = ThemeType.DEFAULT):
        self.theme_type = theme_type
        self.theme_config = self._get_theme_config()
    
    def _get_theme_config(self) -> Dict[str, Any]:
        """Get theme configuration based on theme type."""
        themes = {
            ThemeType.DEFAULT: {
                "colors": {
                    "primary": "#2E86AB",
                    "secondary": "#A23B72",
                    "background": "#FFFFFF",
                    "text": "#333333"
                },
                "fonts": {
                    "title": "Arial",
                    "body": "Arial",
                    "code": "Courier New"
                },
                "layout": {
                    "slide_margin": "1em",
                    "title_size": "2.5em",
                    "subtitle_size": "1.8em",
                    "body_size": "1.2em"
                }
            },
            ThemeType.CORPORATE: {
                "colors": {
                    "primary": "#1E3A8A",
                    "secondary": "#059669",
                    "background": "#F9FAFB",
                    "text": "#111827"
                },
                "fonts": {
                    "title": "Helvetica",
                    "body": "Helvetica",
                    "code": "Monaco"
                },
                "layout": {
                    "slide_margin": "0.8em",
                    "title_size": "2.2em",
                    "subtitle_size": "1.6em",
                    "body_size": "1.1em"
                }
            },
            ThemeType.ACADEMIC: {
                "colors": {
                    "primary": "#7C3AED",
                    "secondary": "#DC2626",
                    "background": "#FFFFFF",
                    "text": "#374151"
                },
                "fonts": {
                    "title": "Times New Roman",
                    "body": "Times New Roman",
                    "code": "Computer Modern"
                },
                "layout": {
                    "slide_margin": "1.2em",
                    "title_size": "2.8em",
                    "subtitle_size": "2.0em",
                    "body_size": "1.3em"
                }
            },
            ThemeType.MINIMAL: {
                "colors": {
                    "primary": "#000000",
                    "secondary": "#6B7280",
                    "background": "#FFFFFF",
                    "text": "#000000"
                },
                "fonts": {
                    "title": "Helvetica Light",
                    "body": "Helvetica Light",
                    "code": "Menlo"
                },
                "layout": {
                    "slide_margin": "2em",
                    "title_size": "3em",
                    "subtitle_size": "2em",
                    "body_size": "1.4em"
                }
            },
            ThemeType.DARK: {
                "colors": {
                    "primary": "#60A5FA",
                    "secondary": "#34D399",
                    "background": "#1F2937",
                    "text": "#F9FAFB"
                },
                "fonts": {
                    "title": "Arial",
                    "body": "Arial",
                    "code": "Fira Code"
                },
                "layout": {
                    "slide_margin": "1em",
                    "title_size": "2.5em",
                    "subtitle_size": "1.8em",
                    "body_size": "1.2em"
                }
            }
        }
        
        return themes.get(self.theme_type, themes[ThemeType.DEFAULT])
    
    def get_css_variables(self) -> str:
        """Generate CSS variables for the theme."""
        css_vars = ":root {\n"
        
        # Color variables
        for name, value in self.theme_config["colors"].items():
            css_vars += f"  --theme-{name}: {value};\n"
        
        # Font variables
        for name, value in self.theme_config["fonts"].items():
            css_vars += f"  --font-{name}: '{value}';\n"
        
        # Layout variables
        for name, value in self.theme_config["layout"].items():
            css_vars += f"  --{name.replace('_', '-')}: {value};\n"
        
        css_vars += "}\n"
        return css_vars
    
    def get_reveal_js_config(self) -> Dict[str, Any]:
        """Get Reveal.js specific configuration for the theme."""
        return {
            "theme": self.theme_type.value,
            "transition": "slide",
            "backgroundTransition": "fade",
            "center": True,
            "controls": True,
            "progress": True,
            "history": True,
            "hash": True
        }
    
    def get_beamer_config(self) -> Dict[str, Any]:
        """Get Beamer specific configuration for the theme."""
        return {
            "theme": "default",
            "colortheme": "default",
            "fonttheme": "default"
        }
    
    def apply_to_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Apply theme configuration to presentation metadata."""
        if "format" not in metadata:
            metadata["format"] = {}
        
        # Apply to revealjs format
        if "revealjs" in metadata["format"]:
            metadata["format"]["revealjs"].update(self.get_reveal_js_config())
        
        # Apply to beamer format  
        if "beamer" in metadata["format"]:
            metadata["format"]["beamer"].update(self.get_beamer_config())
        
        return metadata
