"""HTML generation utilities for ePy_docs.

Provides HTML configuration, CSS generation, and styling utilities
with centralized configuration management and template-based CSS generation.
"""

from typing import Dict, Any
from pathlib import Path


class HtmlGenerator:
    """Unified HTML generation engine with cached configuration."""
    
    def __init__(self):
        self._config_cache = {}
        self._css_cache = {}
    
    def get_html_config(self, layout_name: str = 'classic', **kwargs) -> Dict[str, Any]:
        """Generate complete HTML configuration for Quarto."""
        cache_key = f"html_config_{layout_name}"
        
        if cache_key not in self._config_cache:
            from ePy_docs.core._config import get_config_section
            
            # Get base HTML configuration
            html_config = get_config_section('html')
            base_config = html_config.get('quarto_config', {})
            
            # Apply layout-specific overrides
            layout_config = html_config.get('layouts', {}).get(layout_name, {})
            
            # Merge configurations
            config = {**base_config, **layout_config}
            self._config_cache[cache_key] = config
        
        # Apply runtime overrides
        final_config = {**self._config_cache[cache_key], **kwargs}
        return final_config
    
    def get_html_theme(self, layout_name: str = 'classic') -> str:
        """Get recommended Quarto HTML theme for layout."""
        from ePy_docs.core._config import get_config_section
        
        html_config = get_config_section('html')
        theme_map = html_config.get('theme_mappings', {})
        
        return theme_map.get(layout_name, 'default')
    
    def generate_css(self, layout_name: str = 'classic') -> str:
        """Generate CSS stylesheet for layout using configuration-based templates."""
        cache_key = f"css_{layout_name}"
        
        if cache_key not in self._css_cache:
            css_content = self._build_css(layout_name)
            self._css_cache[cache_key] = css_content
        
        return self._css_cache[cache_key]
    
    def _build_css(self, layout_name: str) -> str:
        """Build CSS from configuration and templates."""
        from ePy_docs.core._config import get_layout_colors, get_font_css_config, get_layout
        from ePy_docs.core._config import get_config_section
        
        # Get configurations
        layout = get_layout(layout_name)
        colors = get_layout_colors(layout_name)
        font_css = get_font_css_config(layout_name)
        
        # Get CSS templates from configuration
        html_config = get_config_section('html')
        css_templates = html_config.get('css_templates', {})
        
        # Build font family
        font_family = self._build_font_family(layout)
        
        # Generate CSS sections
        css_sections = []
        
        # Header comment
        css_sections.append(f"/* ePy_docs Generated Stylesheet - {layout_name} Layout */")
        
        # Font CSS
        if font_css:
            css_sections.append(font_css)
        
        # Variables section
        css_sections.append(self._generate_css_variables(colors))
        
        # Component styles from templates
        for section_name, template in css_templates.items():
            css_section = self._apply_template(template, {
                'font_family': font_family,
                'primary_color': colors.get('primary', '#333'),
                'secondary_color': colors.get('secondary', '#666'),
                'background_color': colors.get('background', '#fff')
            })
            css_sections.append(css_section)
        
        return '\n\n'.join(css_sections)
    
    def _build_font_family(self, layout: Dict[str, Any]) -> str:
        """Build font-family CSS value from layout configuration."""
        from ePy_docs.core._config import get_config_section
        
        format_config = get_config_section('format')
        font_families = format_config.get('font_families', {})
        
        font_family_key = layout.get('font_family', 'sans_technical')
        
        if font_family_key in font_families:
            font_config = font_families[font_family_key]
            primary_font = font_config['primary']
            fallback = font_config.get('fallback', 'sans-serif')
            return f"'{primary_font}', {fallback}"
        
        # Fallback to generic
        return font_family_key if font_family_key in ['serif', 'sans-serif', 'monospace'] else 'sans-serif'
    
    def _generate_css_variables(self, colors: Dict[str, str]) -> str:
        """Generate CSS custom properties from colors."""
        variables = []
        variables.append(":root {")
        for key, value in colors.items():
            variables.append(f"    --color-{key}: {value};")
        variables.append("}")
        return '\n'.join(variables)
    
    def _apply_template(self, template: str, variables: Dict[str, str]) -> str:
        """Apply variables to CSS template."""
        result = template
        for key, value in variables.items():
            result = result.replace(f"{{{key}}}", value)
        return result
    
    def save_css_file(self, css_content: str, output_path: Path) -> Path:
        """Save CSS content to file."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(css_content)
        
        return output_path


# Global generator instance
_generator = HtmlGenerator()


# Pure Delegation API - Maintains backward compatibility
def get_html_config(layout_name: str = 'classic', **kwargs) -> Dict[str, Any]:
    """Generate complete HTML configuration for Quarto."""
    return _generator.get_html_config(layout_name, **kwargs)


def get_html_theme(layout_name: str = 'classic') -> str:
    """Get recommended Quarto HTML theme for layout."""
    return _generator.get_html_theme(layout_name)


def generate_css(layout_name: str = 'classic') -> str:
    """Generate CSS stylesheet for layout using configuration-based templates."""
    return _generator.generate_css(layout_name)


def save_css_file(css_content: str, output_path: Path) -> Path:
    """Save CSS content to file."""
    return _generator.save_css_file(css_content, output_path)
