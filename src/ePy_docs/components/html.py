"""HTML rendering module for ePy_docs.

Handles HTML-specific rendering logic using only JSON configuration.
"""
from typing import Dict, Any
import os
import subprocess
import re

from ePy_docs.components.text import _load_text_config, _get_current_layout_config
from ePy_docs.components.setup import _load_cached_files, _resolve_config_path

class HTMLRenderer:
    """Handles HTML rendering using Quarto with configuration from JSON only."""
    
    def __init__(self):
        """Initialize HTML renderer with JSON configuration only."""
        self.config = _load_cached_files(_resolve_config_path('html', False), False)
    
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
        self.layout_config = _get_current_layout_config(sync_files=sync_files)
        self.text_config = self.layout_config.get('text', {})
        self.headers_config = self.layout_config.get('headers', {})
    
    def convert(self, content: str) -> str:
        """Convert markdown content to HTML using JSON configuration."""
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
        """Convert markdown to HTML using JSON configuration."""
        html_content = content
        
        # Headers - using configuration from text.json
        for level in ['h4', 'h3', 'h2', 'h1']:
            if level in self.headers_config:
                header_config = self.headers_config[level]
                font_size = header_config.get('fontSize', 16)
                margin = f"{header_config.get('spaceBefore', 10)}px 0 {header_config.get('spaceAfter', 6)}px 0"
                
                pattern = '^' + '#' * int(level[1:]) + r' (.+)$'
                replacement = f'<{level} style="font-size: {font_size}px; margin: {margin};">\\1</{level}>'
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
        
        for line in lines:
            stripped = line.strip()
            
            if not stripped:
                processed_lines.append('')
                continue
                
            if (stripped.startswith('<') and stripped.endswith('>')) or stripped.startswith('</'):
                processed_lines.append(line)
                continue
                
            if '<' in stripped and '>' in stripped:
                processed_lines.append(f'<p style="font-size: {font_size}px; line-height: {line_height};">{stripped}</p>')
                continue
                
            if stripped and not any(stripped.startswith(tag) for tag in ['<h1>', '<h2>', '<h3>', '<h4>', '<ul>', '<ol>', '<li>', '<div']):
                processed_lines.append(f'<p style="font-size: {font_size}px; line-height: {line_height};">{stripped}</p>')
            else:
                processed_lines.append(line)
        
        return '\n'.join(processed_lines)
