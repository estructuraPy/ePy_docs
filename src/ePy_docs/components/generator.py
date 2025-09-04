"""
Document generation utilities for ePy_docs.

This module provides functions to generate documents in various formats
(markdown, HTML, PDF, QMD, TEX) with all logic centralized and reusable.
"""

import os
import json
from typing import List, Optional, Dict, Any
from pathlib import Path

from ePy_docs.components.quarto import QuartoConverter, cleanup_quarto_files_directories

class CleanDocumentGenerator:
    """Clean document generator - JSON configuration only."""
    
    def __init__(self, sync_files: bool = True):
        """Initialize with sync_files parameter."""
        self.sync_files = sync_files
        self._load_configurations()
    
    def _load_configurations(self) -> None:
        """Load all required configurations from JSON files."""
        from ePy_docs.components.setup import _load_cached_files, _resolve_config_path
        from pathlib import Path
        
        # # Using centralized configuration _load_cached_files
        setup_config_path = Path(__file__).parent / 'setup.json'
        self.setup_config = _load_cached_files(str(setup_config_path), sync_files=self.sync_files)  #  PURIFICACIÓN ABSOLUTA
        
        # Load component configurations using centralized system _load_cached_files
        try:
            from ePy_docs.components.colors import get_colors_config
            self.colors_config = get_colors_config(sync_files=self.sync_files)  # PURIFICADO: Use get_colors_config
        except Exception:
            self.colors_config = {}
        
        try:
            pages_path = _resolve_config_path('pages', sync_files=self.sync_files)  # page -> pages
            self.page_config = _load_cached_files(pages_path, sync_files=self.sync_files)
        except Exception:
            self.page_config = {}
        
        try:
            math_path = _resolve_config_path('math', sync_files=self.sync_files)  # format -> math
            self.format_config = _load_cached_files(math_path, sync_files=self.sync_files)
        except Exception:
            self.format_config = {}
        
        try:
            notes_path = _resolve_config_path('notes', sync_files=self.sync_files)
            self.notes_config = _load_cached_files(notes_path, sync_files=self.sync_files)
        except Exception:
            self.notes_config = {}
    
    def get_layout_name(self) -> str:
        """Get current layout from pages.json."""
        from ePy_docs.components.pages import get_layout_name
        return get_layout_name(sync_files=self.sync_files)
    
    def get_layout_colors(self, layout_name: str) -> Dict[str, Any]:
        """Get color configuration for layout."""
        layout_colors = self.colors_config["layout_styles"].get(layout_name)
        if not layout_colors:
            available = list(self.colors_config["layout_styles"].keys())
            raise ValueError(f"Layout '{layout_name}' not found in colors.json. Available: {available}")
        return layout_colors
    
    def get_output_directory(self, dir_type: str) -> str:
        """Get output directory from setup.json."""
        from ePy_docs.components.setup import get_absolute_output_directories
        output_dirs = get_absolute_output_directories()
        return output_dirs[dir_type]
    
    def generate_css_styles(self, layout_name: str) -> str:
        """Generate CSS styles for layout with enhanced callouts."""
        from ePy_docs.components.colors import get_color
        colors = self.get_layout_colors(layout_name)
        
        # Convert RGB arrays to CSS colors
        def rgb_to_css(rgb_array):
            return f"rgb({rgb_array[0]}, {rgb_array[1]}, {rgb_array[2]})"
        
        css = f"""/* Layout: {layout_name} */
body {{
    font-family: Arial, sans-serif;
    font-size: 14px;
    line-height: 1.6;
    background-color: {rgb_to_css(colors['background_color'])};
    color: {rgb_to_css(colors['normal'])};
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}}

h1 {{
    color: {rgb_to_css(colors['h1'])};
    font-size: 24px;
    font-weight: bold;
    margin: 20px 0 15px 0;
}}

h2 {{
    color: {rgb_to_css(colors['h2'])};
    font-size: 20px;
    font-weight: bold;
    margin: 18px 0 12px 0;
}}

h3 {{
    color: {rgb_to_css(colors['h3'])};
    font-size: 16px;
    font-weight: bold;
    margin: 15px 0 10px 0;
}}

.caption {{
    color: {rgb_to_css(colors['caption'])};
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
    background-color: rgba({colors['h1'][0]}, {colors['h1'][1]}, {colors['h1'][2]}, 0.08);
    border-left-color: {rgb_to_css(colors['h1'])};
}}

.callout-note .callout-title {{
    color: {rgb_to_css(colors['h1'])};
}}

.callout-warning {{
    background-color: rgba(255, 193, 7, 0.08);
    border-left-color: {get_color('status_warning.medium', 'hex')};
}}

.callout-warning .callout-title {{
    color: {get_color('status_warning.medium_dark', 'hex')};
}}

.callout-tip {{
    background-color: rgba({colors['h2'][0]}, {colors['h2'][1]}, {colors['h2'][2]}, 0.08);
    border-left-color: {rgb_to_css(colors['h2'])};
}}

.callout-tip .callout-title {{
    color: {rgb_to_css(colors['h2'])};
}}

.callout-important {{
    background-color: rgba(220, 53, 69, 0.08);
    border-left-color: {get_color('status_negative.medium', 'hex')};
}}

.callout-important .callout-title {{
    color: {get_color('status_negative.medium', 'hex')};
}}

.callout-success {{
    background-color: rgba(25, 135, 84, 0.08);
    border-left-color: {get_color('status_positive.medium', 'hex')};
}}

.callout-success .callout-title {{
    color: {get_color('status_positive.medium', 'hex')};
}}

.callout-info {{
    background-color: rgba({colors['h3'][0]}, {colors['h3'][1]}, {colors['h3'][2]}, 0.08);
    border-left-color: {rgb_to_css(colors['h3'])};
}}

.callout-info .callout-title {{
    color: {rgb_to_css(colors['h3'])};
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
    border: 1px solid {rgb_to_css(colors['caption'])};
}}

th, td {{
    padding: 8px;
    text-align: left;
}}

th {{
    background-color: {rgb_to_css(colors['h2'])};
    color: white;
}}
"""
        return css
    
    def generate_document_clean(self, content: str, title: str, layout_name: str, 
                               html: bool = False, pdf: bool = False, 
                               output_filename: str = None) -> Dict[str, str]:
        """Generate documents using only JSON configuration."""
        
        # Get output directory from setup.json
        output_dir = self.get_output_directory('report')
        
        # Create filename
        if output_filename:
            base_filename = output_filename
        else:
            base_filename = f"report_{layout_name}"
        
        results = {}
        
        try:
            if html:
                html_path = self._generate_html_clean(content, title, layout_name, output_dir, base_filename)
                results['html'] = html_path
                
            if pdf:
                pdf_path = self._generate_pdf_clean(content, title, layout_name, output_dir, base_filename)
                results['pdf'] = pdf_path
                
        except Exception as e:
            raise RuntimeError(f"Document generation failed: {str(e)}")
        
        return results
    
    def _generate_html_clean(self, content: str, title: str, layout_name: str, 
                            output_dir: str, base_filename: str) -> str:
        """Generate HTML using clean configuration."""
        
        # Generate CSS
        css_content = self.generate_css_styles(layout_name)
        css_filename = f"{base_filename}.css"
        css_path = os.path.join(output_dir, css_filename)
        
        with open(css_path, 'w', encoding='utf-8') as f:
            f.write(css_content)
        
        # Convert markdown to HTML
        html_content_body = self._convert_markdown_to_html(content)
        
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
    
    def _convert_markdown_to_html(self, content: str) -> str:
        """Convert markdown content to HTML with callout styling."""
        import re
        
        # Convert headers
        content = re.sub(r'^# (.+)$', r'<h1>\1</h1>', content, flags=re.MULTILINE)
        content = re.sub(r'^## (.+)$', r'<h2>\1</h2>', content, flags=re.MULTILINE)
        content = re.sub(r'^### (.+)$', r'<h3>\1</h3>', content, flags=re.MULTILINE)
        
        # Split content by double newlines to handle blocks
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
                # Convert to paragraph
                html_blocks.append(f'<p>{block}</p>')
        
        return '\n\n'.join(html_blocks)
    
    def _generate_pdf_clean(self, content: str, title: str, layout_name: str, 
                           output_dir: str, base_filename: str) -> str:
        """Generate PDF using existing system - simplified for functionality."""
        
        # For now, just skip PDF generation to test HTML first
        # This can be enhanced later with proper Quarto integration
        pdf_path = os.path.join(output_dir, f"{base_filename}.pdf")
        
        # Create a placeholder file to indicate PDF generation was attempted
        with open(pdf_path.replace('.pdf', '_pdf_placeholder.txt'), 'w', encoding='utf-8') as f:
            f.write(f"PDF generation placeholder for {title} - Layout: {layout_name}")
        
        return pdf_path

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
    
    Citation style is automatically determined from the current layout in pages.json.
    
    Args:
        sync_files: Whether to sync reference files or not
    
    Returns:
        The citation style that will be used
    """
    # Get default citation style from current layout in pages.json
    from ePy_docs.components.references import get_default_citation_style
    citation_style = get_default_citation_style()
    
    # Sync reference files based on citation style - centralized control
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
    from ePy_docs.components.pages import get_full_project_config
    from ePy_docs.components.setup import _load_cached_files
    
    project_config = get_full_project_config()
    # # Using centralized configuration _load_cached_files
    # Load setup config from core directory
    from pathlib import Path
    setup_config_path = Path(__file__).parent / 'setup.json'
    setup_config = _load_cached_files(str(setup_config_path), sync_files=False)  #  PURIFICACIÓN ABSOLUTA
    
    title = setup_config['report_config']['project_title']
    
    # Handle consultants array - use first consultant as author
    consultants = project_config['consultants']
    author = consultants[0]['name']
    
    return title, author

def generate_qmd_file(content: str, base_filename: str = 'document',
                      citation_style: str = None, sync_files: bool = True) -> str:
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
        
        converter = QuartoConverter()
        qmd_path = converter.markdown_to_qmd(
            content, title=title, author=author,
            output_file=f"{base_filename}.qmd",
            sync_files=sync_files
        )
        return qmd_path
    except Exception:
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

def generate_html_file(markdown_path: str, base_filename: str, citation_style: str, clean_temp: bool = True, sync_files: bool = True) -> str:
    """Generate HTML file from Markdown.
    
    Args:
        markdown_path: Path to Markdown file
        base_filename: Base filename (without extension)
        citation_style: Citation style to use
        clean_temp: Whether to clean temporary files
        sync_files: Whether to read configuration from local JSON files
        
    Returns:
        Path to generated HTML file
    """
    title, author = get_project_metadata()
    
    converter = QuartoConverter()
    html_path = f"{base_filename}.html"
    
    converter.convert_markdown_to_html(
        markdown_content=markdown_path, title=title, author=author,
        output_file=html_path,
        clean_temp=clean_temp
    )
    
    return html_path

def generate_pdf_file(markdown_path: str, base_filename: str, citation_style: str, clean_temp: bool = True, sync_files: bool = True) -> str:
    """Generate PDF file from Markdown.
    
    Args:
        markdown_path: Path to Markdown file
        base_filename: Base filename (without extension)
        citation_style: Citation style to use
        clean_temp: Whether to clean temporary files
        sync_files: Whether to read configuration from local JSON files
        
    Returns:
        Path to generated PDF file
    """
    title, author = get_project_metadata()
    
    converter = QuartoConverter()
    pdf_path = f"{base_filename}.pdf"
    
    converter.convert_markdown_to_pdf(
        markdown_content=markdown_path, title=title, author=author,
        output_file=pdf_path,
        clean_temp=clean_temp
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

def cleanup_temporary_files(markdown_path: Optional[str], markdown_requested: bool) -> None:
    """Clean up temporary files that were not explicitly requested.
    
    Args:
        markdown_path: Path to markdown file (if created)
        markdown_requested: Whether markdown output was explicitly requested
    """
    if not markdown_requested and markdown_path and os.path.exists(markdown_path):
        os.remove(markdown_path)

def generate_documents_clean(content: str, title: str = "Document", 
                           html: bool = False, pdf: bool = False,
                           output_filename: str = None, sync_files: bool = True) -> Dict[str, str]:
    """Generate documents using only JSON configuration - no hardcoded values.
    
    Args:
        content: Document content
        title: Document title
        html: Generate HTML file
        pdf: Generate PDF file
        output_filename: Custom filename for output files
        sync_files: Whether to use synchronized configuration files
        
    Returns:
        Dictionary with paths to generated files
    """
    
    # Use clean generator
    generator = CleanDocumentGenerator(sync_files=sync_files)
    layout_name = generator.get_layout_name()
    
    return generator.generate_document_clean(
        content=content,
        title=title,
        layout_name=layout_name,
        html=html,
        pdf=pdf,
        output_filename=output_filename
    )

def generate_documents(content: str, file_path: str, 
                      markdown: bool = False, html: bool = False, pdf: bool = False, 
                      qmd: bool = False, tex: bool = False,
                      output_filename: str = None, sync_files: bool = True, output_dir: str = None) -> None:
    """Generate documents in requested formats.
    
    This is the main function that coordinates the entire document generation process.
    Citation style is automatically determined from the layout configured in pages.json.
    
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
        generate_qmd_file(content, base_filename, citation_style, sync_files=sync_files)
    
    # Generate TEX file if requested - create it BEFORE conversions to avoid cleanup
    if tex:
        generate_tex_file(content, base_filename)
    
    # Generate markdown file if requested or needed for conversions
    markdown_path = None
    if markdown or html or pdf:
        markdown_path = generate_markdown_file(content, base_filename)
    
    # Generate other formats if requested
    if html or pdf:
        # If QMD or TEX was requested, don't clean temp files to preserve our files
        clean_temp = not (qmd or tex)

        if html:
            generate_html_file(markdown_path, base_filename, citation_style, clean_temp, sync_files=sync_files)

        if pdf:
            generate_pdf_file(markdown_path, base_filename, citation_style, clean_temp, sync_files=sync_files)

    # Remove temporary markdown file if not explicitly requested
    cleanup_temporary_files(markdown_path, markdown)
    
    # Final verification and recreation for requested files
    recreate_missing_files(content, base_filename, citation_style, qmd, tex, sync_files=sync_files)
    
    # Final cleanup: remove any Quarto-generated _files directories
    cleanup_quarto_files_directories(base_filename, file_path)
