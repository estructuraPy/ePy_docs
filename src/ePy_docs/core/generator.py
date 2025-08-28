"""
Document generation utilities for ePy_docs.

This module provides functions to generate documents in various formats
(markdown, HTML, PDF, QMD, TEX) with all logic centralized and reusable.
"""

import os
from typing import List, Optional

from ePy_docs.components.page import get_full_project_config
from ePy_docs.core.quarto import QuartoConverter, cleanup_quarto_files_directories


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
    
    Citation style is automatically determined from the current layout in page.json.
    
    Returns:
        The citation style that will be used
    """
    # Get default citation style from current layout in page.json
    from ePy_docs.components.references import get_default_citation_style
    citation_style = get_default_citation_style()
    
    # Sync reference files based on citation style
    from ePy_docs.components.page import sync_ref
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
            from ePy_docs.core.setup import get_current_project_config
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
    from ePy_docs.core.setup import load_setup_config
    
    project_config = get_full_project_config()
    setup_config = load_setup_config()
    
    title = setup_config['report_config']['project_title']
    
    # Handle consultants array - use first consultant as author
    consultants = project_config['consultants']
    author = consultants[0]['name']
    
    return title, author


def generate_qmd_file(content: str, base_filename: str = 'document',
                      citation_style: str = None) -> str:
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
            output_file=f"{base_filename}.qmd"
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


def generate_html_file(markdown_path: str, base_filename: str, citation_style: str, clean_temp: bool = True) -> str:
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


def generate_pdf_file(markdown_path: str, base_filename: str, citation_style: str, clean_temp: bool = True) -> str:
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


def cleanup_temporary_files(markdown_path: Optional[str], markdown_requested: bool) -> None:
    """Clean up temporary files that were not explicitly requested.
    
    Args:
        markdown_path: Path to markdown file (if created)
        markdown_requested: Whether markdown output was explicitly requested
    """
    if not markdown_requested and markdown_path and os.path.exists(markdown_path):
        os.remove(markdown_path)


def generate_documents(content: str, file_path: str, 
                      markdown: bool = False, html: bool = False, pdf: bool = False, 
                      qmd: bool = False, tex: bool = False,
                      output_filename: str = None, output_dir: str = None) -> None:
    """Generate documents in requested formats.
    
    This is the main function that coordinates the entire document generation process.
    Citation style is automatically determined from the layout configured in page.json.
    
    Args:
        content: Document content to generate
        file_path: Original file path
        markdown: Generate .md file
        html: Generate .html file
        pdf: Generate .pdf file
        qmd: Generate .qmd file (Quarto Markdown)
        tex: Generate .tex file (LaTeX)
        output_filename: Custom filename for output files (without extension)
        sync_files: Whether to read configuration from local JSON files
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
        generate_qmd_file(content, base_filename, citation_style)
    
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
            generate_html_file(markdown_path, base_filename, citation_style, clean_temp)

        if pdf:
            generate_pdf_file(markdown_path, base_filename, citation_style, clean_temp)

    # Remove temporary markdown file if not explicitly requested
    cleanup_temporary_files(markdown_path, markdown)
    
    # Final verification and recreation for requested files
    recreate_missing_files(content, base_filename, citation_style, qmd, tex)
    
    # Final cleanup: remove any Quarto-generated _files directories
    cleanup_quarto_files_directories(base_filename, file_path)
