"""Document generation utilities for ePy_docs.

This module provides functions to generate documents in various formats
with all logic centralized and reusable.
"""

import os
import json
from typing import List, Optional, Dict, Any
from pathlib import Path

from ePy_docs.components.quarto import QuartoConverter, cleanup_quarto_files_directories

def generate_css_styles_pure(layout_name: str, sync_files: bool = True) -> str:
    """Generate CSS styles for layout with enhanced callouts."""
    from ePy_docs.components.text import get_text_config
    from ePy_docs.components.colors import get_colors_config
    
    # Get colors configuration from COLORS kingdom official office
    colors_config = get_colors_config(sync_files=sync_files)
    
    # Get layout-specific colors
    layout_colors = colors_config['layout_styles'][layout_name]
    
    # Get TEXT kingdom configuration for fonts
    text_config = get_text_config(sync_files=sync_files)
    layout_config = text_config['layout_styles'][layout_name]
    
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


def convert_markdown_to_html_pure(content: str, sync_files: bool = True) -> str:
    """Convert markdown content to HTML with callout styling and mathematical notation."""
    import re
    
    # Apply mathematical notation processing first using HTML format for web output
    from ePy_docs.components.format import format_superscripts
    try:
        content = format_superscripts(content, 'html', sync_files)
    except Exception as e:
        print(f"WARNING: Mathematical processing failed in generator: {e}")
        pass
    
    # Convert headers
    content = re.sub(r'^# (.+)$', r'<h1>\1</h1>', content, flags=re.MULTILINE)
    content = re.sub(r'^## (.+)$', r'<h2>\1</h2>', content, flags=re.MULTILINE)
    content = re.sub(r'^### (.+)$', r'<h3>\1</h3>', content, flags=re.MULTILINE)
    
    # Split content by double newlines to handle blocks, but preserve line breaks within blocks
    blocks = content.split('\n\n')
    html_blocks = []
    
    for block in blocks:
        block = block.strip()
        if not block:
            continue
            
        # Check if block is already HTML (contains HTML callouts)
        if block.startswith('<div class="callout'):
            # It's a callout, keep as-is
            html_blocks.append(block)
        elif block.startswith('<h'):
            # It's a header, keep as-is
            html_blocks.append(block)
        else:
            # Convert to paragraph, but preserve line breaks within the paragraph
            # Replace single newlines with <br> to preserve user formatting
            formatted_block = block.replace('\n', '<br>\n')
            html_blocks.append(f'<p>{formatted_block}</p>')
    
    return '\n\n'.join(html_blocks)


def generate_html_clean_pure(content: str, title: str, layout_name: str, 
                            output_dir: str, base_filename: str, sync_files: bool = True) -> str:
    """Generate HTML using clean configuration."""
    
    # Generate CSS
    css_content = generate_css_styles_pure(layout_name, sync_files=sync_files)
    css_filename = f"{base_filename}.css"
    css_path = os.path.join(output_dir, css_filename)
    
    with open(css_path, 'w', encoding='utf-8') as f:
        f.write(css_content)
    
    # Convert markdown to HTML
    html_content_body = convert_markdown_to_html_pure(content, sync_files=sync_files)
    
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
                           output_dir: str, base_filename: str, sync_files: bool = True,
                           document_type: str = "report") -> str:
    """Generate PDF using direct file operations."""
    from ePy_docs.components.quarto import QuartoConverter
    from ePy_docs.components.pdf import PDFRenderer
    from ePy_docs.components.pages import set_current_layout
    
    # Temporarily set layout for PDFRenderer compatibility
    set_current_layout(layout_name)
    
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
    from ePy_docs.components.setup import get_absolute_output_directories
    output_dirs = get_absolute_output_directories(document_type=document_type)
    return output_dirs[dir_type]


def get_current_layout_name_pure(sync_files: bool = True) -> str:
    """Get current layout from configuration."""
    from ePy_docs.components.pages import get_layout_name
    return get_layout_name(sync_files=sync_files)


def generate_document_clean_pure(content: str, title: str, layout_name: str, 
                                html: bool = False, pdf: bool = False, 
                                output_filename: str = None, sync_files: bool = True, 
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
        base_filename = f"report_{layout_name}"
    
    results = {}
    
    try:
        if html:
            html_path = generate_html_clean_pure(content, title, layout_name, output_dir, base_filename, sync_files=sync_files)
            results['html'] = html_path
            
        if pdf:
            pdf_path = generate_pdf_clean_pure(content, title, layout_name, output_dir, base_filename, sync_files=sync_files, document_type=document_type)
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
    
    def __init__(self, sync_files: bool = True):
        """Initialize with sync_files parameter."""
        self.sync_files = sync_files
    
    def get_layout_name(self) -> str:
        """Get current layout from pages.json."""
        return get_current_layout_name_pure(sync_files=self.sync_files)
    
    def get_output_directory(self, dir_type: str) -> str:
        """Get output directory from setup configuration."""
        return get_output_directory_pure(dir_type)
    
    def generate_css_styles(self, layout_name: str) -> str:
        """Generate CSS styles for layout with enhanced callouts."""
        return generate_css_styles_pure(layout_name, sync_files=self.sync_files)
    
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
            output_filename=output_filename,
            sync_files=self.sync_files
        )
    
    def _generate_html_clean(self, content: str, title: str, layout_name: str, 
                            output_dir: str, base_filename: str) -> str:
        """Generate HTML using clean configuration."""
        return generate_html_clean_pure(
            content=content,
            title=title,
            layout_name=layout_name,
            output_dir=output_dir,
            base_filename=base_filename,
            sync_files=self.sync_files
        )
    
    def _convert_markdown_to_html(self, content: str) -> str:
        """Convert markdown content to HTML with callout styling and mathematical notation."""
        return convert_markdown_to_html_pure(content, sync_files=self.sync_files)
    
    def _generate_pdf_clean(self, content: str, title: str, layout_name: str, 
                           output_dir: str, base_filename: str) -> str:
        """Generate PDF using existing system - simplified for functionality."""
        return generate_pdf_clean_pure(
            content=content,
            title=title,
            layout_name=layout_name,
            output_dir=output_dir,
            base_filename=base_filename,
            sync_files=self.sync_files
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

def setup_citation_style(sync_files: bool = True) -> str:
    """Setup and sync citation style files.
    
    Citation style is automatically determined from current layout configuration.
    
    Args:
        sync_files: Whether to sync reference files or not
    
    Returns:
        The citation style that will be used
    """
    from ePy_docs.components.references import get_default_citation_style
    citation_style = get_default_citation_style()
    
    from ePy_docs.components.pages import sync_ref
    sync_ref(citation_style, sync_files=sync_files)
    
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
            from ePy_docs.components.setup import get_current_project_config
            current_config = get_current_project_config()
            if current_config:
                # Use existing project configuration with project's sync_files setting
                sync_files = current_config.settings.sync_files
                report_filename = current_config.get_report_filename('dummy', sync_files=sync_files).replace('.dummy', '')
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
    from ePy_docs.components.project_info import get_constitutional_project_info
    from ePy_docs.components.setup import get_setup_config
    
    # Get constitutional project info (default to report for backward compatibility)
    constitutional_info = get_constitutional_project_info(document_type="report", sync_files=False)
    setup_config = get_setup_config(sync_files=False)

    title = setup_config['report_config']['project_title']
    
    # Handle authors array - use first author
    authors = constitutional_info.get('authors', [])
    author = authors[0]['name'] if authors else 'Author Name'
    
    return title, author

def generate_qmd_file(content: str, base_filename: str = 'document',
                      citation_style: str = None, sync_files: bool = True, document_type: str = "report") -> str:
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

def generate_html_file(markdown_path: str, base_filename: str, citation_style: str, sync_files: bool = True, document_type: str = "report") -> str:
    """Generate HTML file from Markdown.
    
    Args:
        markdown_path: Path to Markdown file
        base_filename: Base filename (without extension)
        citation_style: Citation style to use
        sync_files: Whether to read configuration from local JSON files
        
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

def generate_pdf_file(markdown_path: str, base_filename: str, citation_style: str, sync_files: bool = True, document_type: str = "report") -> str:
    """Generate PDF file from Markdown.
    
    Args:
        markdown_path: Path to Markdown file
        base_filename: Base filename (without extension)
        citation_style: Citation style to use
        sync_files: Whether to read configuration from local JSON files
        
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
                          qmd: bool = False, tex: bool = False, sync_files: bool = True) -> None:
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
            generate_qmd_file(content, base_filename, citation_style, sync_files=sync_files)
    
    if tex:
        tex_path = f"{base_filename}.tex"
        if not os.path.exists(tex_path):
            generate_tex_file(content, base_filename)

def generate_documents_clean(content: str, title: str = "Document", 
                           html: bool = False, pdf: bool = False,
                           output_filename: str = None, sync_files: bool = True,
                           layout_name: str = "academic", output_dir: str = None,
                           document_type: str = "report") -> Dict[str, str]:
    """Generate documents using configuration with universal layout_styles.
    
    Args:
        content: Document content
        title: Document title
        html: Generate HTML file
        pdf: Generate PDF file
        output_filename: Custom filename for output files
        sync_files: Whether to use synchronized configuration files
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
        sync_files=sync_files,
        output_dir=output_dir,
        document_type=document_type
    )

def generate_documents(content: str, file_path: str, 
                      markdown: bool = False, html: bool = False, pdf: bool = False, 
                      qmd: bool = False, tex: bool = False,
                      output_filename: str = None, sync_files: bool = True, output_dir: str = None,
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
        sync_files: Whether to read configuration from local JSON files and sync reference files
        output_dir: Optional output directory (overrides file_path directory when output_filename is provided)
    """
    # Validation
    validate_output_formats(markdown, html, pdf, qmd, tex)
    
    # Setup - citation style determined automatically from layout
    citation_style = setup_citation_style(sync_files=sync_files)
    prepare_output_directory(file_path)
    base_filename = determine_base_filename(file_path, output_filename, output_dir)
    
    # Generate QMD file if requested
    if qmd:
        generate_qmd_file(content, base_filename, citation_style, sync_files=sync_files, document_type=document_type)
    
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
            generate_html_file(markdown_path, base_filename, citation_style, sync_files=sync_files, document_type=document_type)

        if pdf:
            generate_pdf_file(markdown_path, base_filename, citation_style, sync_files=sync_files, document_type=document_type)

    recreate_missing_files(content, base_filename, citation_style, qmd, tex, sync_files=sync_files)
    
    # Final cleanup: remove any Quarto-generated _files directories
    cleanup_quarto_files_directories(base_filename, file_path)
