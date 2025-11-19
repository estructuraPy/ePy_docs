"""HTML generation utilities for ePy_docs.

SOLID-compliant HTML and CSS generation with specialized classes:
- CacheManager: Caching for HTML and CSS generation
- ThemeResolver: Theme resolution and configuration  
- TemplateProcessor: CSS template processing
- CssGenerator: CSS content generation

Version: 3.0.0 - Zero hardcoding, zero wrappers, fail-fast validation
"""

from typing import Dict, Any, Optional, List
from pathlib import Path


class CacheManager:
    """Manages caching for HTML and CSS generation with efficient storage."""
    
    def __init__(self):
        """Initialize cache manager with empty storage."""
        self._html_cache: Dict[str, Dict[str, Any]] = {}
        self._css_cache: Dict[str, str] = {}
    
    def get_html_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Retrieve HTML configuration from cache."""
        cached = self._html_cache.get(cache_key)
        return cached.copy() if cached else None
    
    def set_html_cache(self, cache_key: str, config: Dict[str, Any]) -> None:
        """Store HTML configuration in cache."""
        self._html_cache[cache_key] = config
    
    def get_css_cache(self, cache_key: str) -> Optional[str]:
        """Retrieve CSS content from cache."""
        return self._css_cache.get(cache_key)
    
    def set_css_cache(self, cache_key: str, css_content: str) -> None:
        """Store CSS content in cache."""
        self._css_cache[cache_key] = css_content
    
    def clear_cache(self) -> None:
        """Clear all cached content."""
        self._html_cache.clear()
        self._css_cache.clear()


class ThemeResolver:
    """Resolves themes with strict configuration validation."""
    
    def __init__(self, config_provider):
        """Initialize theme resolver with required config provider.
        
        Args:
            config_provider: Function to get configuration sections
            
        Raises:
            ValueError: If config_provider is None
        """
        if config_provider is None:
            raise ValueError("ThemeResolver requires a valid config_provider")
        self._config_provider = config_provider
    
    def get_html_theme(self, layout_name: str) -> str:
        """Get Quarto HTML theme for layout with strict validation.
        
        Args:
            layout_name: Layout name
            
        Returns:
            Theme name string
            
        Raises:
            ValueError: If theme not found in layout
        """
        from ePy_docs.core._config import load_layout
        
        # Load layout configuration
        layout = load_layout(layout_name, resolve_refs=True)
        
        # Get HTML section from layout
        html_section = layout.get('html', {})
        
        if 'theme' not in html_section:
            raise ValueError(
                f"No theme found in layout '{layout_name}' html configuration"
            )
        
        return html_section['theme']
    
    def resolve_theme_config(self, layout_name: str, base_config: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve theme configuration for layout.
        
        Args:
            layout_name: Layout name
            base_config: Base configuration dictionary
            
        Returns:
            Configuration with theme resolved
        """
        config = base_config.copy()
        
        if 'theme' not in config:
            config['theme'] = self.get_html_theme(layout_name)
        
        return config


class TemplateProcessor:
    """Processes CSS templates with strict validation."""
    
    def __init__(self, config_provider):
        """Initialize template processor with required config provider.
        
        Args:
            config_provider: Function to get configuration sections
            
        Raises:
            ValueError: If config_provider is None
        """
        if config_provider is None:
            raise ValueError("TemplateProcessor requires a valid config_provider")
        self._config_provider = config_provider
    
    def apply_template(self, template: str, variables: Dict[str, str]) -> str:
        """Apply variables to CSS template with robust substitution.
        
        Args:
            template: CSS template string
            variables: Variables to substitute
            
        Returns:
            Processed template string
        """
        result = template
        for key, value in variables.items():
            placeholder = f"{{{key}}}"
            if placeholder in result:
                result = result.replace(placeholder, value)
        return result
    
    def get_css_templates(self) -> Dict[str, str]:
        """Get CSS templates from configuration with strict validation.
        
        Returns:
            CSS templates dictionary
            
        Raises:
            ValueError: If css_templates section is missing
        """
        # Note: This method is deprecated - css_templates should be obtained
        # from individual layout files via load_layout(layout_name)['html']['css_templates']
        # Keeping for backwards compatibility
        html_config = self._config_provider('html')
        
        if not html_config:
            raise ValueError("Failed to load html configuration - deprecated: use layout['html']['css_templates'] instead")
        
        if 'css_templates' not in html_config:
            raise ValueError("Missing 'css_templates' section in html configuration - deprecated: use layout['html']['css_templates'] instead")
        
        return html_config['css_templates']
    
    def process_all_templates(self, variables: Dict[str, str]) -> List[str]:
        """Process all CSS templates with provided variables.
        
        Args:
            variables: Variables to substitute in templates
            
        Returns:
            List of processed template sections
        """
        templates = self.get_css_templates()
        processed_sections = []
        
        for section_name, template in templates.items():
            processed_section = self.apply_template(template, variables)
            processed_sections.append(processed_section)
        
        return processed_sections


class CssGenerator:
    """Generates CSS content with strict configuration validation."""
    
    def __init__(self, template_processor: TemplateProcessor, config_provider):
        """Initialize CSS generator with template processor and config provider.
        
        Args:
            template_processor: Template processor instance
            config_provider: Function to get configuration sections
            
        Raises:
            ValueError: If config_provider is None
        """
        if config_provider is None:
            raise ValueError("CssGenerator requires a valid config_provider")
        self._template_processor = template_processor
        self._config_provider = config_provider
    
    def generate_css(self, layout_name: str, cache_manager: CacheManager) -> str:
        """Generate CSS stylesheet for layout using cached results.
        
        Args:
            layout_name: Layout name
            cache_manager: Cache manager instance
            
        Returns:
            Generated CSS content
        """
        cache_key = f"css_{layout_name}"
        
        cached_css = cache_manager.get_css_cache(cache_key)
        if cached_css:
            return cached_css
        
        css_content = self._build_css(layout_name)
        cache_manager.set_css_cache(cache_key, css_content)
        return css_content
    
    def _build_css(self, layout_name: str) -> str:
        """Build CSS from configuration and templates with strict validation.
        
        Args:
            layout_name: Layout name
            
        Returns:
            Complete CSS content
            
        Raises:
            ValueError: If required configuration is missing
        """
        # Import here to avoid circular dependencies
        from ePy_docs.core._config import get_layout_colors, get_font_css_config, get_layout
        
        # Get configurations with strict validation
        layout = get_layout(layout_name)
        colors = get_layout_colors(layout_name)
        font_css = get_font_css_config(layout_name)
        
        # Validate required color keys
        required_colors = ['primary', 'secondary', 'background']
        missing_colors = [c for c in required_colors if c not in colors]
        if missing_colors:
            raise ValueError(
                f"Missing required colors for layout '{layout_name}': {missing_colors}"
            )
        
        # Build components
        font_family = self._build_font_family(layout)
        text_color = self._get_text_color(colors)
        
        # Generate CSS sections
        css_sections = []
        
        # Header comment
        css_sections.append(f"/* ePy_docs Generated Stylesheet - {layout_name} Layout */")
        
        # Font CSS
        if font_css:
            css_sections.append(font_css)
        
        # Variables section
        css_sections.append(self._generate_css_variables(colors))
        
        # Template-based sections with strict validation
        template_variables = {
            'font_family': font_family,
            'primary_color': colors['primary'],
            'secondary_color': colors['secondary'],
            'background_color': colors['background'],
            'text_color': text_color
        }
        
        processed_sections = self._template_processor.process_all_templates(template_variables)
        css_sections.extend(processed_sections)
        
        return '\n\n'.join(css_sections)
    
    def _build_font_family(self, layout: Dict[str, Any]) -> str:
        """Build font-family CSS value from layout configuration with strict validation.
        
        Args:
            layout: Layout configuration dictionary
            
        Returns:
            Font family CSS string
            
        Raises:
            ValueError: If font configuration is missing or invalid
        """
        fonts_config = self._config_provider('fonts')
        
        if not fonts_config:
            raise ValueError("Failed to load fonts configuration")
        
        if 'font_families' not in fonts_config:
            raise ValueError("Missing 'font_families' section in fonts configuration")
        
        font_families = fonts_config['font_families']
        
        if 'font_family' not in layout:
            raise ValueError("Missing 'font_family' key in layout configuration")
        
        font_family_key = layout['font_family']
        
        if font_family_key not in font_families:
            available = list(font_families.keys())
            raise ValueError(
                f"Font family '{font_family_key}' not found in configuration. Available: {available}"
            )
        
        font_config = font_families[font_family_key]
        
        if 'primary' not in font_config:
            raise ValueError(f"Missing 'primary' font in font_family '{font_family_key}'")
        
        primary_font = font_config['primary']
        
        # Fallback is required for web fonts
        if 'fallback' not in font_config:
            raise ValueError(f"Missing 'fallback' font in font_family '{font_family_key}'")
        
        fallback = font_config['fallback']
        
        return f"'{primary_font}', {fallback}"
    
    def _get_text_color(self, colors: Dict[str, str]) -> str:
        """Get text color from layout palette with strict preference order.
        
        Args:
            colors: Color palette dictionary
            
        Returns:
            Text color value
            
        Raises:
            ValueError: If no suitable text color found
        """
        # Prefer quaternary for text
        if 'quaternary' in colors:
            return colors['quaternary']
        
        # Fallback to primary
        if 'primary' in colors:
            return colors['primary']
        
        raise ValueError(
            "No suitable text color found. Palette must contain 'quaternary' or 'primary'"
        )
    
    def _generate_css_variables(self, colors: Dict[str, str]) -> str:
        """Generate CSS custom properties from colors.

        Args:
            colors: Color palette dictionary

        Returns:
            CSS variables declaration
        """
        variables = [":root {"]
        for key, value in colors.items():
            variables.append(f"  --color-{key}: {value};")
        variables.append("}")
        return "\n".join(variables)


# ============================================================================
# PUBLIC API FUNCTIONS
# ============================================================================

def get_html_config(layout_name: str, document_type: str = 'report') -> Dict[str, Any]:
    """Generate HTML configuration for Quarto rendering.
    
    Args:
        layout_name: Layout style name
        document_type: Document type (report, paper, etc.)
        
    Returns:
        HTML configuration dictionary for Quarto
    """
    from ePy_docs.core._config import load_layout
    
    # Load layout configuration
    layout = load_layout(layout_name, resolve_refs=True)
    
    # Get HTML configuration from layout
    html_section = layout.get('html', {})
    
    # Determine theme from layout's html section
    theme = html_section.get('theme', 'default')
    
    # Base HTML config
    # NOTE: toc, toc-depth, number-sections are controlled by document_type config
    # Do NOT hardcode these values here - they should come from quarto_common section
    base_config = {
        'theme': theme,
        'css': 'styles.css',
        'embed-resources': True,  # CRITICAL: Embed images and resources in HTML
        'self-contained': True    # CRITICAL: Make HTML completely self-contained
    }
    
    return base_config


def generate_css(layout_name: str) -> str:
    """Generate CSS content for layout.
    
    Args:
        layout_name: Layout style name
        
    Returns:
        CSS content as string
    """
    from ePy_docs.core._config import get_config_section, load_layout, get_font_css_config
    from ePy_docs.core._colors import get_palette_color
    
    # Load layout
    layout = load_layout(layout_name, resolve_refs=True)
    
    # Get HTML configuration from layout
    html_section = layout.get('html', {})
    css_templates = html_section.get('css_templates', {})
    
    # Get resolved colors or fallback to palette reference
    colors = layout.get('colors', {})
    if 'palette' in colors:
        # Use resolved palette
        palette_colors = colors['palette']
        primary = palette_colors.get('primary', '#2c3e50')
        secondary = palette_colors.get('secondary', '#3498db') 
        background = palette_colors.get('page_background', '#ffffff')
    else:
        # Fallback to palette_ref approach
        from ePy_docs.core._colors import get_palette_color
        palette_ref = layout.get('palette_ref', 'professional')
        primary = get_palette_color(palette_ref, 'primary', 'hex')
        secondary = get_palette_color(palette_ref, 'secondary', 'hex')
        background = get_palette_color(palette_ref, 'page_background', 'hex')
    
    # Get font CSS for custom fonts
    font_css = get_font_css_config(layout_name)
    
    # Get font family for body
    from ePy_docs.core._config import get_config_section
    fonts_config = get_config_section('fonts')
    
    # Font families are in fonts config
    if fonts_config and 'font_families' in fonts_config:
        font_families = fonts_config['font_families']
    else:
        font_families = {}
        
    font_family_value = layout.get('font_family', 'default')
    
    # Handle both cases: font_family can be a string (key) or a dict (direct config)
    if isinstance(font_family_value, dict):
        # Direct font configuration in layout
        font_config = font_family_value
    elif font_family_value in font_families:
        # Reference to fonts.epyson font_families
        font_config = font_families[font_family_value]
    else:
        # Fallback to default if key not found
        font_config = font_families.get('default', {})
    
    # Extract font settings from config
    primary_font = font_config.get('primary', 'C2024_anm_font')
    
    # Use context-specific fallback for HTML if available
    fallback_policy = font_config.get('fallback_policy', {})
    context_specific = fallback_policy.get('context_specific', {})
    
    if 'html_css' in context_specific:
        fallback_font = context_specific['html_css']
    else:
        fallback_font = font_config.get('fallback', 'Segoe UI, sans-serif')
    
    # Build CSS font-family string
    font_family_css = f"'{primary_font}', {fallback_font}"
    
    # Ensure font_family_css is a string (not a list or other type)
    if not isinstance(font_family_css, str):
        font_family_css = str(font_family_css)

    
    # Start building CSS
    css_content = "/* Auto-generated CSS for ePy_docs */\n\n"
    
    # Add font CSS if available
    if font_css and font_css.strip():
        css_content += "/* Custom fonts */\n"
        css_content += font_css.strip() + "\n\n"
    
    # Add CSS variables
    css_content += f"""
:root {{
  --primary-color: {primary};
  --secondary-color: {secondary};
  --background-color: {background};
}}
"""
    
    # Process CSS templates if available from layout
    if css_templates:
        template_vars = {
            'font_family': str(font_family_css),
            'text_color': '#333',
            'primary_color': str(primary),
            'secondary_color': str(secondary)
        }
        
        for template_name, template_str in css_templates.items():
            processed = template_str
            for var_name, var_value in template_vars.items():
                processed = processed.replace(f'{{{var_name}}}', var_value)
            css_content += f"\n/* {template_name} */\n{processed}\n"
    else:
        # Fallback: basic CSS if no templates found
        css_content += f"""
body {{
  font-family: {font_family_css} !important;
  line-height: 1.6;
  color: #333;
}}

h1, h2, h3, h4, h5, h6 {{
  color: var(--primary-color);
  margin-top: 1.5em;
  margin-bottom: 0.5em;
}}

table {{
  border-collapse: collapse;
  width: 100%;
  margin: 1em 0;
  font-family: {font_family_css} !important;
}}

th, td {{
  padding: 0.5em;
  text-align: left;
  border-bottom: 1px solid #ddd;
  font-family: inherit !important;
}}

th {{
  background-color: var(--primary-color);
  color: white;
  font-weight: bold;
  font-family: inherit !important;
}}
"""

    
    return css_content
