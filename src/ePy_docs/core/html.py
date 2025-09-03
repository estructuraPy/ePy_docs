"""HTML rendering module for ePy_docs.

Handles HTML-specific rendering logic using only JSON configuration.
NO HARDCODED PATHS - all from setup.json.
"""
from typing import Dict, Any
import os
import subprocess
import re

from ePy_docs.components.text import _load_text_config, _get_layout_text_config
from ePy_docs.components.pages import get_colors_config, get_current_layout
from ePy_docs.core.setup import _load_cached_files, get_filepath

class HTMLRenderer:
    """Handles HTML rendering using Quarto with configuration from JSON only."""
    
    def __init__(self):
        """Initialize HTML renderer with JSON configuration only."""
        # Load HTML config from setup.json paths
        try:
            html_config_path = get_filepath('files.configuration.units.format_json', False)
            self.config = _load_cached_files(html_config_path, False)
        except KeyError:
            raise RuntimeError("HTML configuration not found in setup.json. Check files.configuration.units.format_json path.")
    
    def create_html_yaml_config(self, title: str, author: str) -> Dict[str, Any]:
        """Create HTML-specific YAML configuration from JSON settings."""
        html_config = self.config.get('quarto_html_config', {})
        
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
    """Converts markdown content to HTML for callouts using JSON configuration only."""
    
    def __init__(self, sync_files: bool = False):
        """Initialize converter with text configuration from JSON."""
        try:
            current_layout = get_current_layout()
            
            # Load text configuration for headers from setup.json
            text_config_path = get_filepath('files.configuration.units.format_json', sync_files)
            text_config = _load_cached_files(text_config_path, sync_files)
            self.layout_config = text_config.get('layout_styles', {}).get(current_layout, {})
            self.text_config = self.layout_config.get('text', {})
            self.headers_config = self.layout_config.get('headers', {})
            
            # Load layout-specific colors
            colors_config = get_colors_config(sync_files=sync_files)
            self.layout_colors = colors_config.get('layout_styles', {}).get(current_layout, {}).get('typography', {})
            self.page_background = self.layout_colors.get('background_color', [255, 255, 255])
        except Exception as e:
            # NO FALLBACKS - Explicit failure
            raise RuntimeError(f"Failed to initialize MarkdownToHTMLConverter: {e}")
            self.layout_config = {}
            self.text_config = {}
            self.headers_config = {}
            self.layout_colors = {}
            self.page_background = [255, 255, 255]
    
    def convert(self, content: str) -> str:
        """Convert markdown content to HTML using JSON configuration."""
        if not content:
            return ""
        
        processed = self._normalize_text(content)
        html_content = self._convert_to_html(processed)
        
        # Add layout-specific CSS
        css_styles = self._generate_layout_css()
        if css_styles:
            html_content = f"<style>{css_styles}</style>\n{html_content}"
        
        return html_content
    
    def _generate_layout_css(self) -> str:
        """Generate CSS from layout configuration."""
        if not self.layout_colors:
            return ""
        
        def rgb_to_css(color_list):
            if isinstance(color_list, list) and len(color_list) >= 3:
                return f"rgb({color_list[0]}, {color_list[1]}, {color_list[2]})"
            return "inherit"
        
        css_rules = []
        
        # Page background
        bg_color = rgb_to_css(self.page_background)
        css_rules.append(f"body {{ background-color: {bg_color}; }}")
        
        # Typography colors
        if 'normal' in self.layout_colors:
            normal_color = rgb_to_css(self.layout_colors['normal'])
            css_rules.append(f"body, p {{ color: {normal_color}; }}")
        
        # Header colors
        for header_level in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            if header_level in self.layout_colors:
                header_color = rgb_to_css(self.layout_colors[header_level])
                css_rules.append(f"{header_level} {{ color: {header_color}; }}")
        
        # Caption color
        if 'caption' in self.layout_colors:
            caption_color = rgb_to_css(self.layout_colors['caption'])
            css_rules.append(f".caption, figcaption {{ color: {caption_color}; }}")
        
        return "\n".join(css_rules)
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text using configuration parameters."""
        result = text.strip()
        result = re.sub(r'\r\n', '\n', result)
        result = re.sub(r'\n{3,}', '\n\n', result)
        result = re.sub(r'[ \t]+$', '', result, flags=re.MULTILINE)
        return result
    
    def _convert_to_html(self, content: str) -> str:
        """Convert markdown to HTML using JSON configuration."""
        html_content = content
        
        def rgb_to_css(color_list):
            if isinstance(color_list, list) and len(color_list) >= 3:
                return f"rgb({color_list[0]}, {color_list[1]}, {color_list[2]})"
            return "inherit"
        
        # Headers - using default sizes and layout colors
        header_defaults = {
            'h1': {'fontSize': 28, 'spaceBefore': 20, 'spaceAfter': 12},
            'h2': {'fontSize': 22, 'spaceBefore': 16, 'spaceAfter': 10},
            'h3': {'fontSize': 18, 'spaceBefore': 12, 'spaceAfter': 8},
            'h4': {'fontSize': 16, 'spaceBefore': 10, 'spaceAfter': 6},
            'h5': {'fontSize': 14, 'spaceBefore': 8, 'spaceAfter': 4},
            'h6': {'fontSize': 12, 'spaceBefore': 6, 'spaceAfter': 3}
        }
        
        for level in ['h6', 'h5', 'h4', 'h3', 'h2', 'h1']:  # Process from smallest to largest
            # Get configuration (use defaults if not in text.json)
            if level in self.headers_config:
                header_config = self.headers_config[level]
            else:
                header_config = header_defaults[level]
                
            font_size = header_config.get('fontSize', 16)
            margin = f"{header_config.get('spaceBefore', 10)}px 0 {header_config.get('spaceAfter', 6)}px 0"
            
            # Use layout color if available
            color_style = ""
            if level in self.layout_colors:
                color_style = f" color: {rgb_to_css(self.layout_colors[level])};"
            
            pattern = r'^' + '#' * int(level[1:]) + r' (.+)$'
            replacement = f'<{level} style="font-size: {font_size}px; margin: {margin};{color_style}">\\1</{level}>'
            html_content = re.sub(pattern, replacement, html_content, flags=re.MULTILINE)
        
        # Equations 
        html_content = re.sub(r'\$\$([^$]+?)\$\$', r'<div class="math-block">$$\1$$</div>', html_content)
        html_content = re.sub(r'(?<!\$)\$([^$\n]+?)\$(?!\$)', r'<span class="math-inline">$\1$</span>', html_content)
        
        # Links
        html_content = re.sub(r'\[([^\]]+?)\]\(([^)]+?)\)', r'<a href="\2">\1</a>', html_content)
        
        # Code
        code_style = "background-color: #f6f8fa; padding: 2px 4px; border-radius: 3px; font-family: monospace;"
        html_content = re.sub(r'`([^`]+?)`', rf'<code style="{code_style}">\1</code>', html_content)
        
        # Lists - MUST BE PROCESSED BEFORE bold/italic to avoid conflicts with *
        html_content = self._convert_lists(html_content)
        
        # Bold and italic - AFTER lists to avoid asterisk conflicts
        html_content = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html_content)
        html_content = re.sub(r'(?<!\*)\*([^*]+?)\*(?!\*)', r'<em>\1</em>', html_content)
        
        # Paragraphs
        html_content = self._wrap_paragraphs(html_content)
        
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
    
    def _wrap_paragraphs(self, content: str) -> str:
        """Wrap text in paragraphs using configuration."""
        lines = content.split('\n')
        processed_lines = []
        normal_config = self.text_config.get('normal', {})
        font_size = normal_config.get('fontSize', 12)
        line_height = normal_config.get('lineSpacing', 1.2)
        
        def rgb_to_css(color_list):
            if isinstance(color_list, list) and len(color_list) >= 3:
                return f"rgb({color_list[0]}, {color_list[1]}, {color_list[2]})"
            return "inherit"
        
        # Use layout color for normal text if available
        text_color = ""
        if 'normal' in self.layout_colors:
            text_color = f" color: {rgb_to_css(self.layout_colors['normal'])};"
        
        for line in lines:
            stripped = line.strip()
            
            if not stripped:
                processed_lines.append('')
                continue
                
            if (stripped.startswith('<') and stripped.endswith('>')) or stripped.startswith('</'):
                processed_lines.append(line)
                continue
                
            if '<' in stripped and '>' in stripped:
                processed_lines.append(f'<p style="font-size: {font_size}px; line-height: {line_height};{text_color}">{stripped}</p>')
                continue
                
            if stripped and not any(stripped.startswith(tag) for tag in ['<h1>', '<h2>', '<h3>', '<h4>', '<ul>', '<ol>', '<li>', '<div']):
                processed_lines.append(f'<p style="font-size: {font_size}px; line-height: {line_height};{text_color}">{stripped}</p>')
            else:
                processed_lines.append(line)
        
        return '\n'.join(processed_lines)
