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
        from ePy_docs.core._config import load_layout, get_config_section
        
        # Load layout configuration
        layout = load_layout(layout_name, resolve_refs=True)
        
        # Get quarto config for layout
        quarto_config = get_config_section('quarto')
        layout_quarto = quarto_config.get(layout_name, {})
        
        if 'html_theme' not in layout_quarto:
            raise ValueError(
                f"No html_theme found in quarto config for layout '{layout_name}'"
            )
        
        return layout_quarto['html_theme']
    
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
        """DEPRECATED: CSS templates are now generated dynamically.
        
        This method is kept for backwards compatibility but should not be used.
        CSS generation now happens dynamically based on layout configuration
        and does not rely on hardcoded templates.
        
        Returns:
            Empty dictionary
            
        Raises:
            DeprecationWarning: Always raises to indicate deprecated usage
        """
        raise DeprecationWarning(
            "get_css_templates() is deprecated. CSS is now generated dynamically "
            "based on layout configuration. No hardcoded templates are needed."
        )
    
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
        
        # Validate required color keys (match PDF naming: page_background not background)
        required_colors = ['primary', 'secondary', 'page_background']
        missing_colors = [c for c in required_colors if c not in colors]
        if missing_colors:
            raise ValueError(
                f"Missing required colors for layout '{layout_name}': {missing_colors}"
            )
        
        # Build components
        font_family = self._build_font_family(layout)
        # Use same text color resolution as PDF (quaternary or primary)
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
            'background_color': colors['page_background'],  # Use page_background to match PDF
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
    from ePy_docs.core._config import load_layout, get_config_section
    
    # Load layout configuration
    layout = load_layout(layout_name, resolve_refs=True)
    
    # Get quarto config for layout
    quarto_config = get_config_section('quarto')
    layout_quarto = quarto_config.get(layout_name, {})
    
    # Get theme from quarto config
    theme = layout_quarto.get('html_theme', 'default')
    
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
    """Generate CSS content dynamically from layout configuration.
    
    Generates complete CSS based on:
    - Color palette from colors.epyson
    - Fonts from fonts.epyson
    - Callouts from callouts.epyson
    - Layout-specific settings
    
    No hardcoded templates - everything is built from configuration.
    
    Args:
        layout_name: Layout style name
        
    Returns:
        CSS content as string
    """
    from ePy_docs.core._config import (
        load_layout, 
        get_layout_colors, 
        get_font_css_config,
        get_config_section
    )
    
    # Load layout
    layout = load_layout(layout_name, resolve_refs=True)
    
    # Get colors from palette
    palette_colors = get_layout_colors(layout_name)
    
    # Get font CSS for custom fonts
    font_css = get_font_css_config(layout_name)
    
    # Get font configuration
    fonts_config = get_config_section('fonts')
    font_family_value = layout.get('font_family', 'default')
    
    # Resolve font family
    if isinstance(font_family_value, dict):
        font_config = font_family_value
    else:
        font_config = fonts_config['font_families'][font_family_value]
    
    primary_font = font_config['primary']
    fallback_font = font_config.get('fallback_policy', {}).get('context_specific', {}).get('html_css', font_config['fallback'])
    font_family_css = f"'{primary_font}', {fallback_font}"
    
    # Get callouts configuration
    callouts_config = get_config_section('callouts')
    layout_callouts = callouts_config.get('variants', {}).get(layout_name, {})
    callout_format = layout_callouts.get('format', {})
    callout_variants = layout_callouts.get('callouts', {})
    
    # Start building CSS
    css_parts = []
    
    # Header
    css_parts.append(f"/* ePy_docs Auto-generated CSS - {layout_name} layout */")
    css_parts.append(f"/* Generated from configuration - No hardcoded values */\n")
    
    # Custom fonts
    if font_css and font_css.strip():
        css_parts.append("/* Custom fonts */")
        css_parts.append(font_css.strip())
    
    # CSS Variables
    css_parts.append(_generate_css_variables(palette_colors))
    
    # Body styles
    css_parts.append(_generate_body_styles(font_family_css, palette_colors))
    
    # Heading styles
    css_parts.append(_generate_heading_styles(font_family_css, palette_colors))
    
    # Paragraph and text styles
    css_parts.append(_generate_text_styles(font_family_css))
    
    # Table styles
    css_parts.append(_generate_table_styles(font_family_css, palette_colors))
    
    # Code styles
    css_parts.append(_generate_code_styles(palette_colors))
    
    # Link styles
    css_parts.append(_generate_link_styles(palette_colors))
    
    # Figure styles
    css_parts.append(_generate_figure_styles(font_family_css, palette_colors))
    
    # Callout styles (dynamic from callouts.epyson)
    css_parts.append(_generate_callout_styles(
        layout_name,
        callout_variants,
        callout_format,
        font_family_css,
        palette_colors
    ))
    
    # Bibliography styles
    css_parts.append(_generate_bibliography_styles(palette_colors))
    
    return '\n\n'.join(css_parts)


def _generate_css_variables(colors: Dict[str, str]) -> str:
    """Generate CSS custom properties from color palette."""
    variables = [":root {"]
    for key, value in colors.items():
        variables.append(f"  --color-{key}: {value};")
    variables.append("}")
    return "\n".join(variables)


def _generate_body_styles(font_family: str, colors: Dict[str, str]) -> str:
    """Generate body element styles."""
    return f"""/* Body styles */
body {{
  font-family: {font_family} !important;
  color: {colors['page_text']};
  background-color: {colors['page_background']};
  margin: 1rem;
  line-height: 1.6;
}}"""


def _generate_heading_styles(font_family: str, colors: Dict[str, str]) -> str:
    """Generate heading styles from color palette."""
    return f"""/* Heading styles */
h1 {{
  font-family: {font_family} !important;
  color: {colors['primary']};
  margin-top: 1.5em;
  margin-bottom: 0.5em;
}}

h2 {{
  font-family: {font_family} !important;
  color: {colors['secondary']};
  margin-top: 1.3em;
  margin-bottom: 0.5em;
}}

h3 {{
  font-family: {font_family} !important;
  color: {colors['tertiary']};
  margin-top: 1.2em;
  margin-bottom: 0.5em;
}}

h4 {{
  font-family: {font_family} !important;
  color: {colors['quaternary']};
  margin-top: 1em;
  margin-bottom: 0.5em;
}}

h5 {{
  font-family: {font_family} !important;
  color: {colors['quinary']};
  margin-top: 1em;
  margin-bottom: 0.5em;
}}

h6 {{
  font-family: {font_family} !important;
  color: {colors['senary']};
  margin-top: 1em;
  margin-bottom: 0.5em;
}}"""


def _generate_text_styles(font_family: str) -> str:
    """Generate paragraph and list styles."""
    return f"""/* Text styles */
p {{
  font-family: {font_family} !important;
  line-height: 1.6;
  margin-bottom: 1em;
}}

ul, ol {{
  font-family: {font_family} !important;
  line-height: 1.6;
  margin-bottom: 1em;
}}

li {{
  font-family: {font_family} !important;
}}"""


def _generate_table_styles(font_family: str, colors: Dict[str, str]) -> str:
    """Generate table styles from color palette."""
    return f"""/* Table styles */
table {{
  font-family: {font_family} !important;
  border-collapse: collapse;
  width: 100%;
  margin: 1em 0;
}}

thead th {{
  font-family: {font_family} !important;
  background-color: {colors['table_header']};
  color: {colors['table_header_text']};
  padding: 8px;
  text-align: left;
  font-weight: bold;
}}

tbody tr:nth-child(even) {{
  background-color: {colors['table_stripe']};
}}

tbody tr:nth-child(even) td {{
  color: {colors['table_stripe_text']};
}}

td {{
  font-family: {font_family} !important;
  padding: 8px;
  border-bottom: 1px solid {colors['border_color']};
}}"""


def _generate_code_styles(colors: Dict[str, str]) -> str:
    """Generate code block styles."""
    return f"""/* Code styles */
code, pre {{
  font-family: 'Liberation Mono', 'FreeMono', 'Courier New', monospace;
  background-color: {colors['code_background']};
  color: {colors['code_text']};
  padding: 2px 4px;
  border-radius: 3px;
}}

pre {{
  padding: 1em;
  overflow-x: auto;
}}

pre code {{
  padding: 0;
}}"""


def _generate_link_styles(colors: Dict[str, str]) -> str:
    """Generate link styles from color palette."""
    return f"""/* Link styles */
a {{
  color: {colors['secondary']};
  text-decoration: none;
}}

a:hover {{
  text-decoration: underline;
  color: {colors['primary']};
}}

a:visited {{
  color: {colors['tertiary']};
}}"""


def _generate_figure_styles(font_family: str, colors: Dict[str, str]) -> str:
    """Generate figure and caption styles."""
    return f"""/* Figure styles */
.figure {{
  text-align: center;
  margin: 1rem 0;
}}

.figure-caption {{
  font-family: {font_family} !important;
  color: {colors['caption_color']};
  font-style: italic;
  margin-top: 0.5rem;
  font-size: 0.9em;
}}

figcaption {{
  font-family: {font_family} !important;
  color: {colors['caption_color']};
  font-style: italic;
  text-align: center;
  margin-top: 0.5rem;
  font-size: 0.9em;
}}"""


def _generate_callout_styles(
    layout_name: str,
    callout_variants: Dict[str, Any],
    callout_format: Dict[str, Any],
    font_family: str,
    base_colors: Dict[str, str]
) -> str:
    """Generate callout styles dynamically from callouts.epyson configuration.
    
    Args:
        layout_name: Layout name
        callout_variants: Callout variants for this layout from callouts.epyson
        callout_format: Format settings for callouts (bg_alpha, border, etc.)
        font_family: Font family CSS string
        base_colors: Base color palette
        
    Returns:
        CSS string for all callouts
    """
    from ePy_docs.core._config import get_layout_colors
    
    # Get format settings
    bg_alpha = callout_format.get('bg_alpha', 0.1)
    border_width = callout_format.get('border', {}).get('width_px', 1.0)
    border_style = callout_format.get('border', {}).get('style', 'solid')
    
    css_parts = ["/* Callout styles - Generated from callouts.epyson */"]
    
    for callout_type, callout_config in callout_variants.items():
        palette_name = callout_config.get('palette')
        if not palette_name:
            continue
        
        # Get alpha from callout-specific config or shared default
        alpha = callout_config.get('bg_alpha', bg_alpha)
        
        # Get palette colors
        try:
            callout_palette = get_layout_colors(None, palette_name=palette_name)
            primary_color = callout_palette['primary']
            
            # Convert hex to rgba for background
            if primary_color.startswith('#'):
                r = int(primary_color[1:3], 16)
                g = int(primary_color[3:5], 16)
                b = int(primary_color[5:7], 16)
                bg_color = f'rgba({r}, {g}, {b}, {alpha})'
            else:
                bg_color = primary_color
            
            # Generate callout CSS
            css_parts.append(f"""
.callout-{callout_type} {{
  background-color: {bg_color} !important;
  border-left: 4px {border_style} {primary_color} !important;
  color: {base_colors['page_text']} !important;
  padding: 1rem;
  margin: 1rem 0;
  font-family: {font_family} !important;
  border-radius: 4px;
}}

.callout-{callout_type} > .callout-header {{
  color: {primary_color} !important;
  font-weight: bold;
  margin-bottom: 0.5rem;
  font-family: {font_family} !important;
}}

.callout-{callout_type} p {{
  color: {base_colors['page_text']} !important;
  margin-bottom: 0.5em;
}}

.callout-{callout_type} p:last-child {{
  margin-bottom: 0;
}}""")
        
        except Exception as e:
            # Skip if palette not found
            continue
    
    return '\n'.join(css_parts)


def _generate_bibliography_styles(colors: Dict[str, str]) -> str:
    """Generate bibliography/references styles."""
    return f"""/* Bibliography styles */
#quarto-appendix.default {{
  background-color: transparent !important;
  border: none !important;
}}

.quarto-appendix-contents {{
  background-color: transparent !important;
  color: {colors['page_text']} !important;
}}

.quarto-appendix-contents > * {{
  background-color: transparent !important;
  color: {colors['page_text']} !important;
}}

#quarto-appendix .references,
.references,
#refs {{
  background-color: transparent !important;
  color: {colors['page_text']} !important;
}}

#quarto-appendix .references .csl-entry,
.references .csl-entry,
#refs .csl-entry {{
  color: {colors['page_text']} !important;
  margin-bottom: 0.5em;
}}

.references div,
#refs div {{
  background-color: transparent !important;
  color: {colors['page_text']} !important;
}}"""
