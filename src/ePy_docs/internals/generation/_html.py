"""HTML rendering module for ePy_docs.

Handles HTML-specific rendering logic using kingdom commercial channels.
Purified to use official kingdom APIs only.
Uses universal font system from Format Kingdom.
"""
from typing import Dict, Any
import os
import subprocess
import re

from ePy_docs.internals.formatting._text import get_text_config
from ePy_docs.internals.data_processing._data import load_cached_files
from ePy_docs.config.setup import _resolve_config_path

def get_html_config() -> Dict[str, Any]:
    """Load centralized HTML configuration.
    
    OFICINA COMERCIAL OFICIAL - Reino HTML
    
    Returns:
        Complete HTML configuration dictionary.
    """
    try:
        from ePy_docs.internals.data_processing._data import load_cached_files
    except ImportError:
        raise ImportError("ePy_files library is required. Install with: pip install ePy_files")
        
    config_path = _resolve_config_path('components/html')
    return load_cached_files(config_path)

class HTMLRenderer:
    """Handles HTML rendering using Quarto with configuration from JSON only."""
    
    def __init__(self):
        """Initialize HTML renderer with JSON configuration and universal font system."""
        # Load HTML Kingdom specific configuration
        self.html_config = get_html_config()
    
    def create_html_yaml_config(self, title: str, author: str) -> Dict[str, Any]:
        """Create HTML-specific YAML configuration with universal font system."""
        html_config = self.html_config.get('quarto_html_config', {})
        
        # Get current layout for CSS generation
        from ePy_docs.internals.styling._pages import get_layout_config
        try:
            current_layout = get_layout_config()
            current_layout_name = current_layout.get('name', 'minimal')
        except:
            current_layout_name = 'minimal'  # fallback
        
        # Generate CSS from universal font system
        from ePy_docs.internals.formatting._format import generate_css_font_rules
        css_rules = generate_css_font_rules(current_layout_name)
        
        # Convert CSS rules to stylesheet
        css_content = []
        for selector, rule in css_rules.items():
            css_content.append(f"{selector} {{ {rule}; }}")
        
        # Add CSS to HTML configuration
        if css_content:
            html_config['css'] = css_content
        
        return {
            'title': title,
            'author': author,
            'format': {
                'html': html_config
            }
        }
    
    def render_html(self, qmd_file: str, output_dir: str = None) -> str:
        """Render QMD file to HTML using Quarto."""
        qmd_path = os.path.abspath(qmd_file)
        if not os.path.exists(qmd_path):
            raise FileNotFoundError(f"QMD file not found: {qmd_path}")
        
        cmd = ['quarto', 'render', qmd_path, '--to', 'html']
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        qmd_basename = os.path.splitext(os.path.basename(qmd_path))[0]
        return os.path.join(os.path.dirname(qmd_path), f"{qmd_basename}.html")

class MarkdownToHTMLConverter:
    """Converts markdown content to HTML for callouts using kingdom commercial channels."""
    
    def __init__(self):
        """Initialize converter with configuration from Reino TEXT and universal font system."""
        self.text_config = get_text_config()
        
        # Get current layout
        from ePy_docs.internals.styling._pages import get_layout_config
        try:
            current_layout = get_layout_config()
            self.current_layout_name = current_layout.get('name', 'minimal')
        except:
            self.current_layout_name = 'minimal'
        
        # Get layout typography using universal font system
        from ePy_docs.internals.formatting._format import get_layout_font_requirements
        self.font_requirements = get_layout_font_requirements(self.current_layout_name)
    
    def convert(self, content: str) -> str:
        """Convert markdown content to HTML using kingdom configuration."""
        if not content:
            return ""
        
        processed = self._normalize_text(content)
        html_content = self._convert_to_html(processed)
        
        return html_content
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text using configuration parameters."""
        result = text.strip()
        result = re.sub(r'\r\n', '\n', result)
        result = re.sub(r'\n{3,}', '\n\n', result)
        result = re.sub(r'[ \t]+$', '', result, flags=re.MULTILINE)
        return result
    
    def _convert_to_html(self, content: str) -> str:
        """Convert markdown to HTML using universal font system."""
        html_content = content
        
        # Get layout typography
        layout_typography = self.text_config['layout_styles'][self.current_layout_name]['typography']
        
        # Headers - using universal font system
        for level in ['h4', 'h3', 'h2', 'h1']:
            if level in layout_typography:
                header_config = layout_typography[level].copy()
                
                # Convert size to fontSize if needed
                if 'size' in header_config and 'fontSize' not in header_config:
                    size_str = header_config['size']
                    header_config['fontSize'] = int(size_str.replace('pt', ''))
                
                font_size = header_config.get('fontSize', 16)
                margin = f"{font_size * 0.5}px 0 {font_size * 0.3}px 0"
                
                pattern = '^' + '#' * int(level[1:]) + r' (.+)$'
                replacement = f'<{level} style="font-size: {font_size}px; margin: {margin};">\\1</{level}>'
                html_content = re.sub(pattern, replacement, html_content, flags=re.MULTILINE)
        
        # Equations 
        html_content = re.sub(r'\$\$([^$]+?)\$\$', r'<div class="math-block">$$\1$$</div>', html_content)
        html_content = re.sub(r'(?<!\$)\$([^$\n]+?)\$(?!\$)', r'<span class="math-inline">$\1$</span>', html_content)
        
        # Links
        html_content = re.sub(r'\[([^\]]+?)\]\(([^)]+?)\)', r'<a href="\2">\1</a>', html_content)
        
        # Code - get colors from Reino COLORS using commercial channels
        from ePy_docs.internals.styling._colors import get_colors_config
        colors_config = get_colors_config()
        # Default fallback color for code background
        code_bg_color = "#f5f5f5"  # Light gray fallback
        try:
            # Try to get from palettes configuration
            palettes = colors_config.get('palettes', {})
            if palettes:
                # Use first available palette for code background
                first_palette = list(palettes.values())[0]
                code_bg_color = first_palette.get('background', code_bg_color)
        except:
            pass  # Use fallback color
        
        code_style = f"background-color: {code_bg_color}; padding: 2px 4px; border-radius: 3px; font-family: monospace;"
        html_content = re.sub(r'`([^`]+?)`', rf'<code style="{code_style}">\1</code>', html_content)
        
        # Lists - MUST BE PROCESSED BEFORE bold/italic to avoid conflicts with *
        html_content = self._convert_lists(html_content)
        
        # Bold and italic - AFTER lists to avoid asterisk conflicts
        html_content = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html_content)
        html_content = re.sub(r'(?<!\*)\*([^*]+?)\*(?!\*)', r'<em>\1</em>', html_content)
        
        # TODO: Implement wrap_html_paragraphs if needed for paragraph wrapping
        
        return html_content.strip()
    
    def _convert_lists(self, content: str) -> str:
        """Convert lists using JSON configuration."""
        lines = content.split('\n')
        processed_lines = []
        in_list = False
        list_type = None
        
        for line in lines:
            stripped_line = line.strip()
            
            if re.match(r'^[\*\-\+]\s+', stripped_line):
                if not in_list or list_type == 'ol':
                    if in_list:
                        processed_lines.append('</ol>')
                    processed_lines.append('<ul>')
                    in_list = True
                    list_type = 'ul'
                
                item_content = re.sub(r'^[\*\-\+]\s+', '', stripped_line)
                processed_lines.append(f'<li>{item_content}</li>')
                
            elif re.match(r'^\d+\.\s+', stripped_line):
                if not in_list or list_type == 'ul':
                    if in_list:
                        processed_lines.append('</ul>')
                    processed_lines.append('<ol>')
                    in_list = True
                    list_type = 'ol'
                
                item_content = re.sub(r'^\d+\.\s+', '', stripped_line)
                processed_lines.append(f'<li>{item_content}</li>')
                
            else:
                if in_list:
                    processed_lines.append(f'</{list_type}>')
                    in_list = False
                    list_type = None
                processed_lines.append(line)
        
        if in_list:
            processed_lines.append(f'</{list_type}>')
        
        return '\n'.join(processed_lines)
