"""Slides Configuration and Generation for ePy_docs.

This module handles presentation slides generation using Quarto RevealJS and PowerPoint
output formats. It provides functions to create slides configurations,
generate CSS styles, and set up complete Quarto projects for presentation compilation.
"""
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
import os
import yaml
import shutil
import subprocess
import json

# Import from the page configuration module for shared utilities
from ePy_docs.components.page import (
    get_color, get_project_config, get_config_value, _ConfigManager,
    get_layout_config, get_default_citation_style, validate_csl_style,
    sync_ref, create_css_styles
)
from ePy_docs.components.colors import rgb_to_latex_str


def _load_slides_config() -> Dict[str, Any]:
    """Load slides configuration from slides.json.
    
    Returns:
        Dict containing the slides configuration
        
    Raises:
        ValueError: If configuration file is not found
    """
    config_path = Path(__file__).parent.parent / "components" / "slides.json"
    
    if not config_path.exists():
        raise ValueError(f"Slides configuration file not found: {config_path}")
        
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in slides.json: {e}")


def generate_slides_config(sync_json: bool = True) -> Dict[str, Any]:
    """Generate Quarto RevealJS configuration for presentations.
    
    Args:
        sync_json: Whether to sync JSON files before reading. Defaults to True.
        
    Returns:
        A complete Quarto configuration dictionary for slides generation.
    """
    # Load slides configuration - NO FALLBACKS
    slides_config = _load_slides_config()
    
    # Get layout configuration
    if 'default_layout' not in slides_config:
        raise ValueError("Missing 'default_layout' in slides configuration")
    layout_name = slides_config['default_layout']
    
    if 'layouts' not in slides_config:
        raise ValueError("Missing 'layouts' in slides configuration")
    if layout_name not in slides_config['layouts']:
        raise ValueError(f"Layout '{layout_name}' not found in slides configuration")
    layout_config = slides_config['layouts'][layout_name]
    
    # Get project information - required
    project_info = get_project_config()
    if not project_info:
        raise ValueError("Missing project configuration")
        
    title = project_info['name']
    subtitle = project_info['description'] 
    author_date = project_info['created_date']
    
    # Load component configurations - NO FALLBACKS
    components_dir = Path(__file__).parent.parent / "components"
    
    # Load text configuration for typography
    text_json_path = components_dir / "text.json"
    if not text_json_path.exists():
        raise ValueError(f"Text configuration not found: {text_json_path}")
        
    with open(text_json_path, 'r', encoding='utf-8') as f:
        text_config = json.load(f)
    
    if 'text' not in text_config or 'normal' not in text_config['text']:
        raise ValueError("Missing text.normal configuration in text.json")
    
    normal_text = text_config['text']['normal']
    
    # Load images configuration
    images_json_path = components_dir / "images.json"
    if not images_json_path.exists():
        raise ValueError(f"Images configuration not found: {images_json_path}")
        
    with open(images_json_path, 'r', encoding='utf-8') as f:
        images_config = json.load(f)
        
    # Load equations configuration  
    equations_json_path = components_dir / "equations.json"
    if not equations_json_path.exists():
        raise ValueError(f"Equations configuration not found: {equations_json_path}")
        
    with open(equations_json_path, 'r', encoding='utf-8') as f:
        equations_config = json.load(f)
        
    # Load tables configuration
    tables_json_path = components_dir / "tables.json"
    if not tables_json_path.exists():
        raise ValueError(f"Tables configuration not found: {tables_json_path}")
        
    with open(tables_json_path, 'r', encoding='utf-8') as f:
        tables_config = json.load(f)
    
    # Build Quarto configuration for RevealJS
    config = {
        'project': {
            'type': slides_config['project']['type']  # 'revealjs'
        },
        'lang': slides_config['project']['lang'],
        'title': title,
        'subtitle': subtitle,
        'author': author_date,
        'execute': {
            'echo': slides_config['execute']['echo']
        },
        'format': {
            'revealjs': {
                # Theme and visual settings
                'theme': layout_config['theme'],
                'transition': layout_config['transition'], 
                'background-color': layout_config['background_color'],
                'font-size': layout_config['font_size'],
                
                # Navigation and controls
                'hash': slides_config['format']['revealjs']['hash'],
                'history': slides_config['format']['revealjs']['history'],
                'controls': slides_config['format']['revealjs']['controls'],
                'progress': slides_config['format']['revealjs']['progress'],
                'center': slides_config['format']['revealjs']['center'],
                'touch': slides_config['format']['revealjs']['touch'],
                'loop': slides_config['format']['revealjs']['loop'],
                'rtl': slides_config['format']['revealjs']['rtl'],
                'navigation-mode': slides_config['format']['revealjs']['navigation-mode'],
                'keyboard': slides_config['format']['revealjs']['keyboard'],
                'overview': slides_config['format']['revealjs']['overview'],
                'mouse-wheel': slides_config['format']['revealjs']['mouse-wheel'],
                'hide-inactive-cursor': slides_config['format']['revealjs']['hide-inactive-cursor'],
                'hide-cursor-timeout': slides_config['format']['revealjs']['hide-cursor-timeout'],
                'preview-links': slides_config['format']['revealjs']['preview-links'],
                
                # Slide numbering
                'slide-number': slides_config['format']['revealjs']['slide-number'],
                'show-slide-number': slides_config['format']['revealjs']['show-slide-number'],
                
                # Auto-slide settings
                'auto-slide': slides_config['format']['revealjs']['auto-slide'],
                'auto-slide-stoppable': slides_config['format']['revealjs']['auto-slide-stoppable'],
                'auto-slide-method': slides_config['format']['revealjs']['auto-slide-method'],
                'default-timing': slides_config['format']['revealjs']['default-timing'],
                
                # Display dimensions
                'width': slides_config['format']['revealjs']['width'],
                'height': slides_config['format']['revealjs']['height'],
                'margin': slides_config['format']['revealjs']['margin'],
                'min-scale': slides_config['format']['revealjs']['min-scale'],
                'max-scale': slides_config['format']['revealjs']['max-scale'],
                
                # Figure configurations
                'fig-width': images_config['display']['max_width_inches_html'],
                'fig-height': images_config['display']['max_width_inches_html'] * 0.6,
                'fig-align': images_config['styling']['alignment'].lower(),
                'fig-responsive': images_config['display']['html_responsive'],
                'fig-dpi': images_config['display']['dpi']
            },
            'pptx': {
                'reference-doc': slides_config['format']['pptx']['reference-doc'],
                'slide-level': slides_config['format']['pptx']['slide-level']
            }
        },
        'crossref': {
            'chapters': slides_config['crossref']['chapters'],
            'eq-prefix': equations_config['crossref']['eq-prefix'],
            'eq-labels': slides_config['crossref']['eq-labels'],
            'fig-prefix': images_config['crossref']['fig-prefix'],
            'fig-labels': slides_config['crossref']['fig-labels'],
            'tbl-prefix': tables_config['crossref']['tbl-prefix'],
            'tbl-labels': slides_config['crossref']['tbl-labels']
        }
    }
    
    return config


def create_slides_project(project_dir: Union[str, Path], sync_json: bool = True) -> None:
    """Create a complete Quarto slides project with all necessary files.
    
    Args:
        project_dir: Directory where the slides project will be created
        sync_json: Whether to sync JSON files before creating project
    """
    project_path = Path(project_dir)
    project_path.mkdir(exist_ok=True)
    
    # Generate Quarto configuration
    config = generate_slides_config(sync_json=sync_json)
    
    # Create _quarto.yml file
    quarto_file = project_path / "_quarto.yml"
    with open(quarto_file, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    # Create slides-specific CSS if needed
    css_content = create_slides_css()
    if css_content:
        css_file = project_path / "slides-styles.css" 
        with open(css_file, 'w', encoding='utf-8') as f:
            f.write(css_content)
    
    return project_path


def create_slides_css() -> str:
    """Generate custom CSS for slides based on layout configuration.
    
    Returns:
        CSS content as string
    """
    slides_config = _load_slides_config()
    if 'default_layout' not in slides_config:
        raise ValueError("Missing 'default_layout' in slides configuration")
    layout_name = slides_config['default_layout']
    
    if 'layouts' not in slides_config or layout_name not in slides_config['layouts']:
        raise ValueError(f"Layout '{layout_name}' not found in slides configuration")
    layout = slides_config['layouts'][layout_name]
    
    css_content = f"""/* Custom CSS for ePy_docs Slides - {layout_name} layout */

.reveal {{
    font-family: "{layout['font_family']}";
    font-size: {layout['font_size']};
    color: {layout['text_color']};
    background-color: {layout['background_color']};
}}

.reveal h1, .reveal h2, .reveal h3 {{
    color: {layout['accent_color']};
}}

.reveal h1 {{
    font-size: {layout['title_font_size']};
}}

.reveal h2 {{
    font-size: {layout['subtitle_font_size']};
}}

.reveal .progress {{
    color: {layout['accent_color']};
}}

.reveal .controls {{
    color: {layout['accent_color']};
}}

/* Custom slide classes */
.title-slide {{
    background-color: {layout['accent_color']};
    color: white;
}}

.section-slide {{
    background: linear-gradient(45deg, {layout['background_color']}, {layout['accent_color']});
    color: white;
}}
"""
    
    return css_content


class SlidesStyler:
    """Class for managing slides styling and configuration."""
    
    def __init__(self, layout: str = None):
        """Initialize slides styler with specific layout.
        
        Args:
            layout: Layout name to use. If None, uses default from config.
        """
        self.config = _load_slides_config()
        
        if layout is None:
            if 'default_layout' not in self.config:
                raise ValueError("Missing 'default_layout' in slides configuration")
            self.layout_name = self.config['default_layout']
        else:
            self.layout_name = layout
        
        if 'layouts' not in self.config:
            raise ValueError("Missing 'layouts' in slides configuration")
        if self.layout_name not in self.config['layouts']:
            raise ValueError(f"Layout '{self.layout_name}' not found in slides configuration")
            
        self.layout = self.config['layouts'][self.layout_name]
    
    def get_theme_config(self) -> Dict[str, Any]:
        """Get theme configuration for current layout."""
        return {
            'theme': self.layout['theme'],
            'background_color': self.layout['background_color'],
            'text_color': self.layout['text_color'],
            'accent_color': self.layout['accent_color'],
            'transition': self.layout['transition']
        }
    
    def get_typography_config(self) -> Dict[str, Any]:
        """Get typography configuration for current layout."""
        return {
            'font_size': self.layout['font_size'],
            'title_font_size': self.layout['title_font_size'],
            'subtitle_font_size': self.layout['subtitle_font_size']
        }
    
    def get_dimensions_config(self) -> Dict[str, Any]:
        """Get slide dimensions configuration."""
        slides_format = self.config['format']['revealjs']
        return {
            'width': slides_format['width'],
            'height': slides_format['height'],
            'margin': slides_format['margin'],
            'aspect_ratio': self.config['slide_settings']['dimensions']['aspect_ratio']
        }


def render_slides(source_file: Union[str, Path], output_dir: Union[str, Path] = None, 
                 format_type: str = "revealjs") -> bool:
    """Render slides using Quarto.
    
    Args:
        source_file: Path to the source .qmd file
        output_dir: Output directory. If None, uses same directory as source
        format_type: Output format ('revealjs' or 'pptx')
        
    Returns:
        True if rendering was successful, False otherwise
    """
    source_path = Path(source_file)
    
    if not source_path.exists():
        raise FileNotFoundError(f"Source file not found: {source_path}")
    
    # Build quarto command
    cmd = ["quarto", "render", str(source_path), "--to", format_type]
    
    if output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        cmd.extend(["--output-dir", str(output_path)])
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=source_path.parent)
        
        if result.returncode == 0:
            return True
        else:
            raise RuntimeError(f"Quarto render failed: {result.stderr}")
            
    except subprocess.SubprocessError as e:
        raise RuntimeError(f"Error running Quarto: {e}")
