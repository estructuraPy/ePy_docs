"""Document generation utilities for ePy_docs.

This module provides functions to generate documents in various formats
with all logic centralized and reusable.
"""

import os
import json
import logging
from typing import List, Optional, Dict, Any
from pathlib import Path

from ePy_docs.internals.generation._quarto import QuartoConverter, cleanup_quarto_files_directories

def generate_css_styles_pure(layout_name: str) -> str:
    """Generate CSS styles for layout with enhanced callouts."""
    from ePy_docs.internals.formatting._text import get_text_config
    from ePy_docs.internals.styling._colors import get_colors_config
    
    # Get colors configuration from COLORS kingdom official office
    colors_config = get_colors_config()
    
    # Get layout-specific colors
    layout_colors = colors_config['layout_styles'][layout_name]
    
    # Get TEXT kingdom configuration for fonts
    text_config = get_text_config()
    layout_config = text_config['layout_styles'][layout_name]
    
    # Suppress matplotlib font warnings globally - CONSTITUTIONAL MANDATE
    matplotlib_logger = logging.getLogger('matplotlib.font_manager')
    original_level = matplotlib_logger.level
    matplotlib_logger.setLevel(logging.ERROR)
    
    try:
        # Get font family for body text
        if 'typography' in layout_config and 'normal' in layout_config['typography']:
            font_family_key = layout_config['typography']['normal']['family']
        else:
            raise ValueError(f"Typography configuration missing for layout '{layout_name}'")
            
        # Build font list from font family configuration
        font_config = text_config['font_families'][font_family_key]
        font_list = [font_config['primary']]
        if font_config.get('fallback'):
            fallback_fonts = [f.strip() for f in font_config['fallback'].split(',')]
            font_list.extend(fallback_fonts)
    finally:
        # Restore original logging level
        matplotlib_logger.setLevel(original_level)
    
    # Create CSS font-family string
    css_font_family = ', '.join(font_list)
    
    # Convert RGB arrays to CSS colors
    def rgb_to_css(rgb_array):
        return f"rgb({rgb_array[0]}, {rgb_array[1]}, {rgb_array[2]})"
    
    # Helper function to resolve palette/tone references to actual colors
    def resolve_color_reference(color_ref):
        palette_name = color_ref['palette']
        tone = color_ref['tone']
        return colors_config['palettes'][palette_name][tone]
    
    # Get layout-specific colors by resolving references
    layout_color_config = colors_config['layout_styles'][layout_name]['typography']
    layout_colors = {}
    for key, color_ref in layout_color_config.items():
        layout_colors[key] = resolve_color_reference(color_ref)
    
    # Get status colors from COLORS kingdom and convert to CSS
    warning_medium = rgb_to_css(colors_config['palettes']['status_warning']['medium'])
    warning_dark = rgb_to_css(colors_config['palettes']['status_warning']['medium_dark'])
    negative_medium = rgb_to_css(colors_config['palettes']['status_negative']['medium'])
    positive_medium = rgb_to_css(colors_config['palettes']['status_positive']['medium'])
    
    css = f"""/* Layout: {layout_name} */
body {{
    font-family: {css_font_family};
    font-size: 14px;
    line-height: 1.6;
    background-color: {rgb_to_css(layout_colors['background_color'])};
    color: {rgb_to_css(layout_colors['normal'])};
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}}

h1 {{
    color: {rgb_to_css(layout_colors['h1'])};
    font-size: 24px;
    font-weight: bold;
    margin: 20px 0 15px 0;
}}

h2 {{
    color: {rgb_to_css(layout_colors['h2'])};
    font-size: 20px;
    font-weight: bold;
    margin: 18px 0 12px 0;
}}

h3 {{
    color: {rgb_to_css(layout_colors['h3'])};
    font-size: 16px;
    font-weight: bold;
    margin: 15px 0 10px 0;
}}

.caption {{
    color: {rgb_to_css(layout_colors['caption'])};
    font-size: 12px;
    font-style: italic;
    text-align: center;
}}

/* Enhanced Callout Styles */
.callout {{
    border-radius: 8px;
    padding: 16px;
    margin: 20px 0;
    border-left: 4px solid;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}}

.callout-header {{
    display: flex;
    align-items: center;
    margin-bottom: 12px;
}}

.callout-icon {{
    margin-right: 10px;
    font-size: 1.4em;
    line-height: 1;
}}

.callout-title {{
    font-weight: bold;
    font-size: 1.1em;
    margin: 0;
}}

.callout-content {{
    margin-top: 8px;
}}

.callout-image {{
    max-width: 100%;
    border-radius: 4px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}}

/* Callout Types with Layout-Based Colors */
.callout-note {{
    background-color: rgba({layout_colors['h1'][0]}, {layout_colors['h1'][1]}, {layout_colors['h1'][2]}, 0.08);
    border-left-color: {rgb_to_css(layout_colors['h1'])};
}}

.callout-note .callout-title {{
    color: {rgb_to_css(layout_colors['h1'])};
}}

.callout-warning {{
    background-color: rgba(255, 193, 7, 0.08);
    border-left-color: {warning_medium};
}}

.callout-warning .callout-title {{
    color: {warning_dark};
}}

.callout-tip {{
    background-color: rgba({layout_colors['h2'][0]}, {layout_colors['h2'][1]}, {layout_colors['h2'][2]}, 0.08);
    border-left-color: {rgb_to_css(layout_colors['h2'])};
}}

.callout-tip .callout-title {{
    color: {rgb_to_css(layout_colors['h2'])};
}}

.callout-important {{
    background-color: rgba(220, 53, 69, 0.08);
    border-left-color: {negative_medium};
}}

.callout-important .callout-title {{
    color: {negative_medium};
}}

.callout-success {{
    background-color: rgba(25, 135, 84, 0.08);
    border-left-color: {positive_medium};
}}

.callout-success .callout-title {{
    color: {positive_medium};
}}

.callout-info {{
    background-color: rgba({layout_colors['h3'][0]}, {layout_colors['h3'][1]}, {layout_colors['h3'][2]}, 0.08);
    border-left-color: {rgb_to_css(layout_colors['h3'])};
}}

.callout-info .callout-title {{
    color: {rgb_to_css(layout_colors['h3'])};
}}

img {{
    max-width: 100%;
    height: auto;
    display: block;
    margin: 10px auto;
}}

table {{
    width: 100%;
    border-collapse: collapse;
    margin: 15px 0;
}}

table, th, td {{
    border: 1px solid {rgb_to_css(layout_colors['caption'])};
}}

th, td {{
    padding: 8px;
    text-align: left;
}}

th {{
    background-color: {rgb_to_css(layout_colors['h2'])};
    color: white;
}}
"""
    return css


def convert_markdown_to_html_pure(content: str) -> str:
    """Convert markdown content to HTML with callout styling and mathematical notation."""
    import re
    
    # Apply mathematical notation processing preserving LaTeX equations
    from ePy_docs.internals.formatting._format import format_superscripts
    try:
        # Apply superscript formatting only to text OUTSIDE of LaTeX equations
        # Split content by LaTeX equations to preserve them
        parts = re.split(r'(\$[^$]+\$)', content)
        
        formatted_parts = []
        for i, part in enumerate(parts):
            if i % 2 == 0:  # Even indices are regular text
                # Apply superscript formatting to regular text only
                formatted_part = format_superscripts(part, 'html')
                formatted_parts.append(formatted_part)
            else:  # Odd indices are LaTeX equations - preserve them exactly
                formatted_parts.append(part)
        
        content = ''.join(formatted_parts)
        
    except Exception as e:
        print(f"WARNING: Mathematical processing failed in generator: {e}")
        pass
    
    # Process callouts FIRST (before other markdown)
    # Match pattern: ::: {type}\n## Title (optional)\nContent\n:::
    callout_pattern = r':::\s*\{(\w+)\}\s*\n(?:##\s*(.+?)\n+)?(.*?):::'
    
    def replace_callout(match):
        callout_type = match.group(1).strip()  # note, tip, warning, etc.
        title = match.group(2).strip() if match.group(2) else callout_type.capitalize()
        content_inner = match.group(3).strip() if match.group(3) else ""
        
        # Map callout types to CSS classes and icons
        callout_info = {
            'note': ('📝', '#2563eb', 'Info'),
            'tip': ('💡', '#16a34a', 'Tip'),
            'warning': ('⚠️', '#ea580c', 'Warning'),
            'important': ('❗', '#dc2626', 'Important'),
            'success': ('✅', '#059669', 'Success'),
            'advice': ('💭', '#8b5cf6', 'Advice'),
            'error': ('❌', '#dc2626', 'Error'),
            'info': ('ℹ️', '#0891b2', 'Info'),
            'caution': ('⚠️', '#f59e0b', 'Caution')
        }
        
        icon, color, default_title = callout_info.get(callout_type.lower(), ('📌', '#64748b', 'Note'))
        
        # Use provided title or default
        if not title or title.lower() == callout_type.lower():
            title = default_title
        
        # Process markdown in content (bold, italic, code)
        content_inner = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', content_inner)
        content_inner = re.sub(r'\*(.+?)\*', r'<em>\1</em>', content_inner)
        content_inner = re.sub(r'`([^`]+)`', r'<code>\1</code>', content_inner)
        
        # Convert line breaks to HTML
        content_inner = content_inner.replace('\n', '<br>\n')
        
        return f'''<div class="callout callout-{callout_type.lower()}" style="border-left: 4px solid {color}; padding: 1em; margin: 1em 0; background-color: rgba(0,0,0,0.03); border-radius: 4px;">
    <div class="callout-title" style="font-weight: bold; margin-bottom: 0.5em; color: {color}; font-size: 1.1em;">
        <span style="margin-right: 0.5em;">{icon}</span>{title}
    </div>
    <div class="callout-content" style="color: #374151;">
        {content_inner}
    </div>
</div>'''
    
    content = re.sub(callout_pattern, replace_callout, content, flags=re.DOTALL)
    
    # Convert headers (h4 first to avoid conflicts)
    content = re.sub(r'^#### (.+)$', r'<h4>\1</h4>', content, flags=re.MULTILINE)
    content = re.sub(r'^### (.+)$', r'<h3>\1</h3>', content, flags=re.MULTILINE)
    content = re.sub(r'^## (.+)$', r'<h2>\1</h2>', content, flags=re.MULTILINE)
    content = re.sub(r'^# (.+)$', r'<h1>\1</h1>', content, flags=re.MULTILINE)
    
    # Process inline formatting (bold BEFORE italic to avoid conflicts)
    # Bold: **text** -> <strong>text</strong>
    content = re.sub(r'\*\*([^\*]+?)\*\*', r'<strong>\1</strong>', content)
    # Italic: *text* -> <em>text</em> (but not if already inside strong)
    content = re.sub(r'(?<!</strong>)\*([^\*]+?)\*(?!\*)', r'<em>\1</em>', content)
    
    # Process bibliography blocks BEFORE inline citations
    # Pattern: [@...multiline content...][@...another entry...]...
    # More robust pattern that captures everything between [@ and the next heading or double newline
    def replace_bibliography_block(match):
        """Convert bibliography blocks to HTML reference list."""
        block_content = match.group(1)
        
        # Split by ][@  to get individual entries
        entries = re.split(r'\]\s*\[@', block_content)
        
        html_parts = ['<div class="references" style="margin: 2em 0; padding: 1em; background-color: rgba(0,0,0,0.02); border-radius: 4px;">']
        html_parts.append('<h3 style="margin-top: 0; color: #374151;">Referencias Bibliográficas</h3>')
        html_parts.append('<ol style="padding-left: 1.5em;">')
        
        for entry in entries:
            # Clean up entry
            entry = entry.strip()
            if entry:
                # Remove any remaining [ or ] at start/end
                entry = entry.strip('[]')
                # Process markdown in the entry (italic, bold)
                entry = re.sub(r'\*\*([^\*]+?)\*\*', r'<strong>\1</strong>', entry)
                entry = re.sub(r'\*([^\*]+?)\*', r'<em>\1</em>', entry)
                # Replace newlines with <br> for multiline entries
                entry = entry.replace('\n', '<br>\n')
                html_parts.append(f'  <li style="margin-bottom: 0.8em;">{entry}</li>')
        
        html_parts.append('</ol>')
        html_parts.append('</div>')
        return '\n'.join(html_parts)
    
    # Match bibliography blocks: [@...content...][@...content...]...
    # Captures from first [@ to last ] before a heading or double newline
    content = re.sub(
        r'\[@\s*((?:[^\]]*\]\s*\[@[^\]]*)*[^\]]*)\](?=\s*(?:\n\n|<h\d>|$))',
        replace_bibliography_block,
        content,
        flags=re.DOTALL
    )
    
    # Process inline citations (must be AFTER bibliography blocks)
    # Pattern: [@CSCR2010] or [@CSCR2010, Section 4.5]
    content = re.sub(r'\[@([^\]]+?)\]', r'<cite>[\1]</cite>', content)
    
    # Process links
    content = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', content)
    
    # Process horizontal rules
    content = re.sub(r'^---+$', r'<hr>', content, flags=re.MULTILINE)
    
    # Process code blocks
    def replace_code_block(match):
        lang = match.group(1) or 'text'
        code_content = match.group(2).strip()
        # Escape HTML in code
        code_content = code_content.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        return f'<pre><code class="language-{lang}">{code_content}</code></pre>'
    
    content = re.sub(r'```(\w*)\n(.*?)\n```', replace_code_block, content, flags=re.DOTALL)
    
    # Process inline code
    content = re.sub(r'`([^`]+)`', r'<code>\1</code>', content)
    
    # Process lists (unordered and ordered)
    lines = content.split('\n')
    in_list = False
    result_lines = []
    
    for line in lines:
        # Check for unordered list
        if re.match(r'^[-*]\s+(.+)$', line):
            if not in_list:
                result_lines.append('<ul>')
                in_list = 'ul'
            item = re.sub(r'^[-*]\s+(.+)$', r'\1', line)
            result_lines.append(f'  <li>{item}</li>')
        # Check for ordered list
        elif re.match(r'^\d+\.\s+(.+)$', line):
            if in_list != 'ol':
                if in_list == 'ul':
                    result_lines.append('</ul>')
                result_lines.append('<ol>')
                in_list = 'ol'
            item = re.sub(r'^\d+\.\s+(.+)$', r'\1', line)
            result_lines.append(f'  <li>{item}</li>')
        else:
            if in_list:
                result_lines.append(f'</{in_list}>')
                in_list = False
            result_lines.append(line)
    
    if in_list:
        result_lines.append(f'</{in_list}>')
    
    content = '\n'.join(result_lines)
    
    # Split content by double newlines to handle blocks, but preserve line breaks within blocks
    blocks = content.split('\n\n')
    html_blocks = []
    
    for block in blocks:
        block = block.strip()
        if not block:
            continue
            
        # Check if block is already HTML
        if (block.startswith('<div') or block.startswith('<h') or 
            block.startswith('<ul') or block.startswith('<ol') or
            block.startswith('<pre') or block.startswith('<hr')):
            # It's already HTML, keep as-is
            html_blocks.append(block)
        else:
            # Convert to paragraph, but preserve line breaks within the paragraph
            # Replace single newlines with <br> to preserve user formatting
            formatted_block = block.replace('\n', '<br>\n')
            html_blocks.append(f'<p>{formatted_block}</p>')
    
    return '\n\n'.join(html_blocks)


def generate_html_clean_pure(content: str, title: str, layout_name: str, 
                            output_dir: str, base_filename: str) -> str:
    """Generate HTML using clean configuration."""
    
    # Generate CSS
    css_content = generate_css_styles_pure(layout_name)
    css_filename = f"{base_filename}.css"
    css_path = os.path.join(output_dir, css_filename)
    
    with open(css_path, 'w', encoding='utf-8') as f:
        f.write(css_content)
    
    # Convert markdown to HTML
    html_content_body = convert_markdown_to_html_pure(content)
    
    # Generate HTML content
    html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <link rel="stylesheet" href="{css_filename}">
</head>
<body>
    <div class="container">
        {html_content_body}
    </div>
</body>
</html>"""
    
    html_path = os.path.join(output_dir, f"{base_filename}.html")
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return html_path


def generate_pdf_clean_pure(content: str, title: str, layout_name: str, 
                           output_dir: str, base_filename: str,
                           document_type: str = "report") -> str:
    """Generate PDF using direct file operations."""
    from ePy_docs.internals.generation._quarto import QuartoConverter
    from ePy_docs.internals.generation._pdf import PDFRenderer
    from ePy_docs.internals.styling._pages import set_current_layout
    from ePy_docs.internals.generation._references import get_bibliography_config, get_default_citation_style
    from ePy_docs.internals.styling._pages import sync_ref
    import shutil
    from pathlib import Path
    
    # Temporarily set layout for PDFRenderer compatibility
    set_current_layout(layout_name)
    
    # Setup citation style files before generating QMD
    citation_style = get_default_citation_style(layout_name)
    sync_ref(citation_style)
    
    # CONSTITUTIONAL: Use document_type to determine correct configuration
    converter = QuartoConverter(document_type=document_type)
    qmd_path = os.path.join(output_dir, f"{base_filename}.qmd")
    
    converter.markdown_to_qmd(
        content, 
        title=title, 
        author="Anonymous", 
        output_file=qmd_path
    )
    
    if os.path.exists(qmd_path):
        pdf_renderer = PDFRenderer()
        pdf_path = pdf_renderer.render_pdf(qmd_path, output_dir)
        return pdf_path
    else:
        raise RuntimeError("Failed to generate QMD file")


def get_output_directory_pure(dir_type: str, document_type: str = "report") -> str:
    """Get output directory from setup configuration."""
    from ePy_docs.config.setup import get_absolute_output_directories
    output_dirs = get_absolute_output_directories(document_type=document_type)
    return output_dirs[dir_type]


def get_current_layout_name_pure() -> str:
    """Get current layout from configuration."""
    from ePy_docs.internals.styling._pages import get_layout_name
    return get_layout_name()


def generate_document_clean_pure(content: str, title: str, layout_name: str, 
                                html: bool = False, pdf: bool = False, 
                                output_filename: str = None, 
                                output_dir: str = None, document_type: str = "report") -> Dict[str, str]:
    """Generate documents using only JSON configuration."""
    
    # Use provided output_dir or default to report directory
    if output_dir:
        output_dir = output_dir
    else:
        output_dir = get_output_directory_pure('report', document_type=document_type)
    
    if output_filename:
        base_filename = output_filename
    else:
        # Use title parameter which comes from layout configuration via APIs
        clean_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).replace(' ', '_')
        base_filename = clean_title if clean_title else document_type
    
    results = {}
    
    try:
        if html:
            html_path = generate_html_clean_pure(content, title, layout_name, output_dir, base_filename)
            results['html'] = html_path
            
        if pdf:
            pdf_path = generate_pdf_clean_pure(content, title, layout_name, output_dir, base_filename, document_type=document_type)
            results['pdf'] = pdf_path
            
    except Exception as e:
        raise RuntimeError(f"Document generation failed: {str(e)}")
    
    return results

# =============================================================================
# LEGACY CLASS WRAPPER - Maintains Backward Compatibility  
# =============================================================================

class CleanDocumentGenerator:
    """Clean document generator - JSON configuration only.
    
    LEGACY WRAPPER: For backward compatibility. All actual work is done by pure functions.
    """
    
    def __init__(self):
        """Initialize document generator."""
        pass
    
    def get_layout_name(self) -> str:
        """Get current layout from pages.json."""
        return get_current_layout_name_pure()
    
    def get_output_directory(self, dir_type: str) -> str:
        """Get output directory from setup configuration."""
        return get_output_directory_pure(dir_type)
    
    def generate_css_styles(self, layout_name: str) -> str:
        """Generate CSS styles for layout with enhanced callouts."""
        return generate_css_styles_pure(layout_name)
    
    def generate_document_clean(self, content: str, title: str, layout_name: str, 
                               html: bool = False, pdf: bool = False, 
                               output_filename: str = None) -> Dict[str, str]:
        """Generate documents using only JSON configuration."""
        return generate_document_clean_pure(
            content=content,
            title=title,
            layout_name=layout_name,
            html=html,
            pdf=pdf,
            output_filename=output_filename
        )
    
    def _generate_html_clean(self, content: str, title: str, layout_name: str, 
                            output_dir: str, base_filename: str) -> str:
        """Generate HTML using clean configuration."""
        return generate_html_clean_pure(
            content=content,
            title=title,
            layout_name=layout_name,
            output_dir=output_dir,
            base_filename=base_filename
        )
    
    def _convert_markdown_to_html(self, content: str) -> str:
        """Convert markdown content to HTML with callout styling and mathematical notation."""
        return convert_markdown_to_html_pure(content)
    
    def _generate_pdf_clean(self, content: str, title: str, layout_name: str, 
                           output_dir: str, base_filename: str) -> str:
        """Generate PDF using existing system - simplified for functionality."""
        return generate_pdf_clean_pure(
            content=content,
            title=title,
            layout_name=layout_name,
            output_dir=output_dir,
            base_filename=base_filename
        )


def validate_output_formats(markdown: bool = False, html: bool = False, pdf: bool = False, 
                           qmd: bool = False, tex: bool = False) -> None:
    """Validate that at least one output format is requested.
    
    Args:
        markdown: Generate .md file
        html: Generate .html file
        pdf: Generate .pdf file
        qmd: Generate .qmd file (Quarto Markdown)
        tex: Generate .tex file (LaTeX)
        
    Raises:
        ValueError: If no output formats are requested
    """
    if not any([markdown, html, pdf, qmd, tex]):
        raise ValueError("No output formats requested")

def setup_citation_style() -> str:
    """Setup and sync citation style files.
    
    Citation style is automatically determined from current layout configuration.
    
    Returns:
        The citation style that will be used
    """
    from ePy_docs.internals.generation._references import get_default_citation_style
    citation_style = get_default_citation_style()
    
    from ePy_docs.internals.styling._pages import sync_ref
    sync_ref(citation_style)
    
    return citation_style

def prepare_output_directory(file_path: str) -> None:
    """Create output directory if it doesn't exist.
    
    Args:
        file_path: Path to the main file
    """
    directory = os.path.dirname(file_path)
    if directory:
        os.makedirs(directory, exist_ok=True)

def determine_base_filename(file_path: str, output_filename: Optional[str] = None, output_dir: Optional[str] = None) -> str:
    """Determine the base filename for output files.
    
    Args:
        file_path: Original file path
        output_filename: Custom filename for output files (without extension)
        output_dir: Optional output directory (overrides file_path directory when output_filename is provided)
        
    Returns:
        Base filename to use for output files
    """
    if output_filename:
        # Use provided custom filename with preferred output directory
        if output_dir:
            directory = output_dir
        else:
            directory = os.path.dirname(file_path)
        return os.path.join(directory, output_filename)
    else:
        # Use default behavior - try to get filename from configuration
        directory = os.path.dirname(file_path)
        try:
            from ePy_docs.config.setup import get_current_project_config
            current_config = get_current_project_config()
            if current_config:
                # Use existing project configuration
                report_filename = current_config.get_report_filename('dummy').replace('.dummy', '')
                return os.path.join(directory, report_filename)
            else:
                # Fallback to original file path behavior
                return os.path.splitext(file_path)[0]
        except:
            # Fallback to original file path behavior
            return os.path.splitext(file_path)[0]

def get_project_metadata() -> tuple[str, str]:
    """Get project title and author from configuration.
    
    Returns:
        Tuple of (title, author)
    """
    from ePy_docs.internals.styling._project_info import get_constitutional_project_info
    from ePy_docs.config.setup import get_setup_config
    
    # Get constitutional project info (default to report for backward compatibility)
    constitutional_info = get_constitutional_project_info(document_type="report")
    setup_config = get_setup_config()

    title = setup_config['report_config']['project_title']
    
    # Handle authors array - use first author
    authors = constitutional_info.get('authors', [])
    author = authors[0]['name'] if authors else 'Author Name'
    
    return title, author

def generate_qmd_file(content: str, base_filename: str = 'document',
                      citation_style: str = None, document_type: str = "report") -> str:
    """Generate QMD file from content.
    
    Args:
        content: Markdown content to convert
        base_filename: Base filename (without extension)
        citation_style: Citation style to use (determined from layout)
        
    Returns:
        Path to generated QMD file or None if generation failed
    """
    try:
        title, author = get_project_metadata()
        
        converter = QuartoConverter(document_type=document_type)
        qmd_path = converter.markdown_to_qmd(
            content, title=title, author=author,
            output_file=f"{base_filename}.qmd"
        )
        return qmd_path
    except Exception as e:
        print(f"DEBUG Error in generate_qmd_file: {e}")
        import traceback
        traceback.print_exc()
        return None

def generate_tex_file(content: str, base_filename: str) -> str:
    """Generate TEX file from content.
    
    Args:
        content: Content to write to TEX file
        base_filename: Base filename (without extension)
        
    Returns:
        Path to generated TEX file
    """
    tex_path = f"{base_filename}.tex"
    with open(tex_path, 'w', encoding='utf-8') as f:
        f.write(content)
    return tex_path

def generate_markdown_file(content: str, base_filename: str) -> str:
    """Generate Markdown file from content.
    
    Args:
        content: Content to write to Markdown file
        base_filename: Base filename (without extension)
        
    Returns:
        Path to generated Markdown file
    """
    markdown_path = f"{base_filename}.md"
    with open(markdown_path, 'w', encoding='utf-8') as f:
        f.write(content)
    return markdown_path

def generate_html_file(markdown_path: str, base_filename: str, citation_style: str, document_type: str = "report") -> str:
    """Generate HTML file from Markdown.
    
    Args:
        markdown_path: Path to Markdown file
        base_filename: Base filename (without extension)
        citation_style: Citation style to use
        
    Returns:
        Path to generated HTML file
    """
    title, author = get_project_metadata()
    
    converter = QuartoConverter(document_type=document_type)
    html_path = f"{base_filename}.html"
    
    converter.convert_markdown_to_html(
        markdown_content=markdown_path, title=title, author=author,
        output_file=html_path
    )
    
    return html_path

def generate_pdf_file(markdown_path: str, base_filename: str, citation_style: str, document_type: str = "report") -> str:
    """Generate PDF file from Markdown.
    
    Args:
        markdown_path: Path to Markdown file
        base_filename: Base filename (without extension)
        citation_style: Citation style to use
        
    Returns:
        Path to generated PDF file
    """
    title, author = get_project_metadata()
    
    converter = QuartoConverter(document_type=document_type)
    pdf_path = f"{base_filename}.pdf"
    
    converter.convert_markdown_to_pdf(
        markdown_content=markdown_path, title=title, author=author,
        output_file=pdf_path
    )
    
    return pdf_path

def recreate_missing_files(content: str, base_filename: str, citation_style: str, 
                          qmd: bool = False, tex: bool = False) -> None:
    """Recreate any missing requested files.
    
    Args:
        content: Original content
        base_filename: Base filename (without extension)
        citation_style: Citation style to use
        qmd: Whether QMD file was requested
        tex: Whether TEX file was requested
    """
    if qmd:
        qmd_path = f"{base_filename}.qmd"
        if not os.path.exists(qmd_path):
            generate_qmd_file(content, base_filename, citation_style)
    
    if tex:
        tex_path = f"{base_filename}.tex"
        if not os.path.exists(tex_path):
            generate_tex_file(content, base_filename)

def generate_documents_clean(content: str, title: str = "Document", 
                           html: bool = False, pdf: bool = False,
                           output_filename: str = None,
                           layout_name: str = "academic", output_dir: str = None,
                           document_type: str = "report") -> Dict[str, str]:
    """Generate documents using configuration with universal layout_styles.
    
    Args:
        content: Document content
        title: Document title
        html: Generate HTML file
        pdf: Generate PDF file
        output_filename: Custom filename for output files
        layout_name: Layout to use (default: 'academic')
        
    Returns:
        Dictionary with paths to generated files
    """
    
    # Validate layout_name is one of the 8 universal layout_styles
    valid_layouts = {'academic', 'technical', 'corporate', 'minimal', 
                    'classic', 'scientific', 'professional', 'creative'}
    if layout_name not in valid_layouts:
        raise ValueError(f"Invalid layout_name '{layout_name}'. Must be one of: {sorted(valid_layouts)}")
    
    return generate_document_clean_pure(
        content=content,
        title=title,
        layout_name=layout_name,
        html=html,
        pdf=pdf,
        output_filename=output_filename,
        output_dir=output_dir,
        document_type=document_type
    )

def generate_documents(content: str, file_path: str, 
                      markdown: bool = False, html: bool = False, pdf: bool = False, 
                      qmd: bool = False, tex: bool = False,
                      output_filename: str = None, output_dir: str = None,
                      document_type: str = "report") -> None:
    """Generate documents in requested formats.
    
    This is the main function that coordinates the entire document generation process.
    Citation style is automatically determined from layout configuration.
    
    Args:
        content: Document content to generate
        file_path: Original file path
        markdown: Generate .md file
        html: Generate .html file
        pdf: Generate .pdf file
        qmd: Generate .qmd file (Quarto Markdown)
        tex: Generate .tex file (LaTeX)
        output_filename: Custom filename for output files (without extension)
        output_dir: Optional output directory (overrides file_path directory when output_filename is provided)
    """
    # Validation
    validate_output_formats(markdown, html, pdf, qmd, tex)
    
    # Setup - citation style determined automatically from layout
    citation_style = setup_citation_style()
    prepare_output_directory(file_path)
    base_filename = determine_base_filename(file_path, output_filename, output_dir)
    
    # Generate QMD file if requested
    if qmd:
        generate_qmd_file(content, base_filename, citation_style, document_type=document_type)
    
    # Generate TEX file if requested - create it BEFORE conversions to avoid cleanup
    if tex:
        generate_tex_file(content, base_filename)
    
    # Generate markdown file if requested or needed for conversions
    markdown_path = None
    if markdown or html or pdf:
        markdown_path = generate_markdown_file(content, base_filename)
    
    # Generate other formats if requested
    if html or pdf:
        if html:
            generate_html_file(markdown_path, base_filename, citation_style, document_type=document_type)

        if pdf:
            generate_pdf_file(markdown_path, base_filename, citation_style, document_type=document_type)

    recreate_missing_files(content, base_filename, citation_style, qmd, tex)
    
    # Final cleanup: remove any Quarto-generated _files directories
    cleanup_quarto_files_directories(base_filename, file_path)
