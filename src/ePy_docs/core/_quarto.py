"""
Quarto Integration Module

Handles:
- Quarto YAML generation
- QMD file creation
- Quarto rendering (qmd -> pdf/html)
- Format coordination
"""

from typing import Dict, Any, List, Optional
from pathlib import Path
import subprocess
import yaml


# =============================================================================
# QUARTO YAML GENERATION
# =============================================================================

def generate_quarto_yaml(
    title: str,
    layout_name: str = 'classic',
    document_type: str = 'article',
    output_formats: List[str] = ['pdf', 'html'],
    fonts_dir: Path = None,
    language: str = 'en',
    **kwargs
) -> Dict[str, Any]:
    """
    Generate complete Quarto YAML frontmatter.
    
    Args:
        title: Document title
        layout_name: Layout name ('classic', 'modern', 'handwritten', etc.)
        document_type: Document type ('article', 'report', 'book')
        output_formats: List of output formats ('pdf', 'html')
        fonts_dir: Absolute path to fonts directory (for PDF font loading)
        language: Document language ('en', 'es', 'fr', etc.)
        **kwargs: Additional options (author, subtitle, etc.)
        
    Returns:
        Dictionary with Quarto YAML configuration
    """
    from ePy_docs.core._pdf import get_pdf_config
    from ePy_docs.core._html import get_html_config
    
    # Base metadata
    yaml_config = {
        'title': title,
        'author': kwargs.get('author', 'Anonymous'),
        'lang': language,
    }
    
    # Optional metadata
    if 'subtitle' in kwargs:
        yaml_config['subtitle'] = kwargs['subtitle']
    if 'date' in kwargs:
        yaml_config['date'] = kwargs['date']
    
    # Format configuration
    format_config = {}
    
    if 'pdf' in output_formats:
        format_config['pdf'] = get_pdf_config(
            layout_name=layout_name,
            document_type=document_type,
            fonts_dir=fonts_dir,
            **kwargs
        )
    
    if 'html' in output_formats:
        format_config['html'] = get_html_config(
            layout_name=layout_name,
            **kwargs
        )
    
    yaml_config['format'] = format_config
    
    # Additional Quarto options
    if 'bibliography' in kwargs:
        yaml_config['bibliography'] = kwargs['bibliography']
    if 'csl' in kwargs:
        yaml_config['csl'] = kwargs['csl']
    
    # Crossref configuration
    # For reports, disable chapters to avoid "Chapter #" prefix in headings
    chapters_enabled = kwargs.get('crossref_chapters', True)
    if document_type == 'report':
        chapters_enabled = False
    
    yaml_config['crossref'] = {
        'chapters': chapters_enabled,
        'fig-labels': kwargs.get('crossref_fig_labels', 'arabic'),
        'tbl-labels': kwargs.get('crossref_tbl_labels', 'arabic'),
        'eq-labels': kwargs.get('crossref_eq_labels', 'arabic'),
    }
    
    # Code execution settings
    yaml_config['execute'] = {
        'echo': kwargs.get('echo', False),
        'warning': kwargs.get('warning', False),
        'message': kwargs.get('message', False),
    }
    
    return yaml_config


# =============================================================================
# QMD FILE CREATION
# =============================================================================

def _fix_image_paths_to_absolute(content: str, base_dir: Path) -> str:
    """
    Convert relative image paths to absolute paths for LaTeX compilation.
    
    LuaLaTeX runs from a temporary directory, so relative paths don't work.
    This function converts all relative image paths to absolute paths.
    
    Args:
        content: Markdown content with image references
        base_dir: Base directory to resolve relative paths from
        
    Returns:
        Content with absolute image paths
    """
    import re
    from pathlib import Path
    
    # Pattern to match markdown images: ![alt](path)
    image_pattern = r'!\[([^\]]*)\]\(([^)]+)\)'
    
    def replace_path(match):
        alt_text = match.group(1)
        img_path = match.group(2)
        
        # Skip if already absolute (Windows: C:/ or Unix: /)
        if img_path.startswith(('http://', 'https://', '/', 'C:/', 'c:/')):
            return match.group(0)
        
        # Skip if already has Windows drive letter (any drive)
        if len(img_path) > 1 and img_path[1] == ':':
            return match.group(0)
        
        # Skip if it's a data URL or other special format
        if ':' in img_path and not (len(img_path) > 1 and img_path[1] == ':'):
            return match.group(0)
        
        # Convert relative path to absolute
        # Try to resolve from base_dir first
        candidate_path = (base_dir / img_path).resolve()
        
        # If the path doesn't exist, try going up directories to find the root
        # This handles cases where QMD is in results/report/ but image path is also results/report/...
        if not candidate_path.exists():
            # Try from parent directory
            parent_candidate = (base_dir.parent / img_path).resolve()
            if parent_candidate.exists():
                candidate_path = parent_candidate
            else:
                # Try from grandparent directory
                grandparent_candidate = (base_dir.parent.parent / img_path).resolve()
                if grandparent_candidate.exists():
                    candidate_path = grandparent_candidate
                else:
                    # Keep original resolved path even if doesn't exist
                    candidate_path = (base_dir / img_path).resolve()
        
        # Convert to forward slashes for LaTeX compatibility
        abs_path_str = str(candidate_path).replace('\\', '/')
        
        return f'![{alt_text}]({abs_path_str})'
    
    # Replace all image paths
    fixed_content = re.sub(image_pattern, replace_path, content)
    
    return fixed_content


def create_qmd_file(
    output_path: Path,
    content: str,
    yaml_config: Dict[str, Any],
    fix_image_paths: bool = True,
    layout_name: str = 'classic'
) -> Path:
    """
    Create QMD file with YAML frontmatter and content.
    
    Also generates the styles.css file for HTML rendering with the correct layout.
    
    Args:
        output_path: Path to save QMD file
        content: Markdown content body
        yaml_config: YAML frontmatter configuration
        fix_image_paths: Convert relative image paths to absolute (default: True)
        layout_name: Layout name for CSS generation
        
    Returns:
        Path to created QMD file
    """
    import shutil
    
    # Ensure parent directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Copy custom fonts to output directory if needed for PDF
    # Returns absolute path to fonts directory
    fonts_dir = _copy_layout_fonts_to_output(layout_name, output_path.parent)
    
    # If yaml_config is being passed, update it with fonts_dir if it has PDF config
    if 'format' in yaml_config and 'pdf' in yaml_config['format']:
        # Need to regenerate PDF config with fonts_dir
        from ePy_docs.core._pdf import get_pdf_config
        
        # Extract existing PDF config parameters
        pdf_config = yaml_config['format']['pdf']
        document_type = pdf_config.get('documentclass', 'article')
        
        # Regenerate with fonts_dir
        yaml_config['format']['pdf'] = get_pdf_config(
            layout_name=layout_name,
            document_type=document_type,
            fonts_dir=fonts_dir
        )
    
    # Fix image paths to absolute if requested
    if fix_image_paths:
        # Use the directory where the QMD will be saved as base
        base_dir = output_path.parent
        content = _fix_image_paths_to_absolute(content, base_dir)
    
    # Generate and save CSS file for HTML rendering
    from ePy_docs.core._html import generate_css
    css_content = generate_css(layout_name=layout_name)
    css_path = output_path.parent / 'styles.css'
    with open(css_path, 'w', encoding='utf-8') as f:
        f.write(css_content)
    
    # Generate YAML frontmatter
    yaml_str = yaml.dump(yaml_config, default_flow_style=False, sort_keys=False)
    
    # Combine YAML and content
    qmd_content = f'''---
{yaml_str}---

{content}
'''
    
    # Write to file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(qmd_content)
    
    return output_path


def _copy_layout_fonts_to_output(layout_name: str, output_dir: Path) -> Path:
    """Copy custom fonts required by layout to output directory for PDF rendering.
    
    Returns:
        Path to fonts directory (absolute path)
    """
    import shutil
    from ePy_docs.core._config import get_loader
    
    fonts_dir = output_dir / 'fonts'
    
    try:
        loader = get_loader()
        layout = loader.load_layout(layout_name)
        font_family = layout.get('font_family')
        
        if not font_family:
            return fonts_dir
        
        complete_config = loader.load_complete_config(layout_name)
        font_families = complete_config.get('format', {}).get('font_families', {})
        font_config = font_families.get(font_family)
        
        if not font_config:
            return fonts_dir
        
        primary_font = font_config.get('primary', '')
        font_file_template = font_config.get('font_file_template')
        
        if primary_font and font_file_template:
            # Find source font file
            font_filename = font_file_template.format(font_name=primary_font)
            package_root = Path(__file__).parent.parent
            source_font = package_root / 'config' / 'assets' / 'fonts' / font_filename
            
            if source_font.exists():
                # Create fonts subdirectory in output
                fonts_dir.mkdir(exist_ok=True)
                
                # Copy font file
                dest_font = fonts_dir / font_filename
                shutil.copy2(source_font, dest_font)
                
    except Exception:
        # Don't fail if font copy fails
        pass
    
    return fonts_dir


# =============================================================================
# QUARTO RENDERING
# =============================================================================

def render_qmd(
    qmd_path: Path,
    output_format: Optional[str] = None,
    output_dir: Optional[Path] = None
) -> Path:
    """
    Render QMD file using Quarto.
    
    Args:
        qmd_path: Path to QMD file
        output_format: Specific format to render ('pdf', 'html', or None for all)
        output_dir: Output directory (optional)
        
    Returns:
        Path to output file
        
    Raises:
        RuntimeError: If Quarto rendering fails
    """
    if not qmd_path.exists():
        raise FileNotFoundError(f"QMD file not found: {qmd_path}")
    
    # Build Quarto command
    cmd = ['quarto', 'render', str(qmd_path)]
    
    if output_format:
        cmd.extend(['--to', output_format])
    
    if output_dir:
        cmd.extend(['--output-dir', str(output_dir)])
    
    # Execute Quarto
    try:
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
            cwd=qmd_path.parent
        )
        
        # Determine output file path
        if output_format == 'pdf':
            output_file = qmd_path.with_suffix('.pdf')
        elif output_format == 'html':
            output_file = qmd_path.with_suffix('.html')
        else:
            output_file = qmd_path.parent
        
        return output_file
        
    except subprocess.CalledProcessError as e:
        error_msg = f"Quarto rendering failed:\n{e.stderr}"
        raise RuntimeError(error_msg) from e


def render_to_pdf(qmd_path: Path) -> Path:
    """Render QMD to PDF."""
    return render_qmd(qmd_path, output_format='pdf')


def render_to_html(qmd_path: Path) -> Path:
    """Render QMD to HTML."""
    return render_qmd(qmd_path, output_format='html')


# =============================================================================
# COMPLETE WORKFLOW
# =============================================================================

def create_and_render(
    output_path: Path,
    content: str,
    title: str,
    layout_name: str = 'classic',
    document_type: str = 'article',
    output_formats: List[str] = ['pdf', 'html'],
    language: str = 'en',
    **kwargs
) -> Dict[str, Path]:
    """
    Complete workflow: create QMD and render to specified formats.
    
    Args:
        output_path: Path to save QMD file
        content: Markdown content
        title: Document title
        layout_name: Layout name
        document_type: Document type
        output_formats: List of formats to generate
        language: Document language
        **kwargs: Additional options
        
    Returns:
        Dictionary mapping format names to output file paths
    """
    # Generate YAML configuration
    yaml_config = generate_quarto_yaml(
        title=title,
        layout_name=layout_name,
        document_type=document_type,
        output_formats=output_formats,
        language=language,
        **kwargs
    )
    
    # Create QMD file with CSS generation
    # Don't fix image paths since our tables already generate correct relative paths
    qmd_path = create_qmd_file(output_path, content, yaml_config, fix_image_paths=False, layout_name=layout_name)
    
    # Render to each format
    results = {'qmd': qmd_path}
    
    for fmt in output_formats:
        try:
            output_file = render_qmd(qmd_path, output_format=fmt)
            results[fmt] = output_file
        except Exception as e:
            print(f"Warning: Failed to render {fmt}: {e}")
            results[fmt] = None
    
    return results


# =============================================================================
# UTILITIES
# =============================================================================

def check_quarto_installed() -> bool:
    """
    Check if Quarto is installed and available.
    
    Returns:
        True if Quarto is installed, False otherwise
    """
    try:
        result = subprocess.run(
            ['quarto', '--version'],
            capture_output=True,
            text=True,
            check=False
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False


def get_quarto_version() -> str:
    """
    Get installed Quarto version.
    
    Returns:
        Version string, or 'Not installed' if Quarto not found
    """
    try:
        result = subprocess.run(
            ['quarto', '--version'],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except (FileNotFoundError, subprocess.CalledProcessError):
        return "Not installed"


# =============================================================================
# QUARTO FILE PROCESSING FOR WRITER
# =============================================================================

def process_quarto_file(
    file_path: str,
    include_yaml: bool = False,
    fix_image_paths: bool = True,
    convert_tables: bool = True,
    output_dir: str = None,
    figure_counter: int = 1,
    document_type: str = 'report',
    writer_instance = None
) -> None:
    """
    Process Quarto file and add to writer.
    
    Automatically processes:
    - Markdown tables: Converts to styled image tables
    - Images: Extracts caption from markdown and adds as figure
    - Text content: Preserves as-is
    - YAML frontmatter: Optionally included or stripped
    
    Args:
        file_path: Path to Quarto file
        include_yaml: Whether to include YAML frontmatter
        fix_image_paths: Whether to fix image paths
        convert_tables: Whether to convert tables to styled images
        output_dir: Output directory
        figure_counter: Current figure counter
        document_type: Document type
        writer_instance: DocumentWriter instance
    """
    import re
    import os
    from pathlib import Path
    
    # Read file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Skip YAML if requested
    if not include_yaml and content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            content = parts[2].strip()
    
    if not writer_instance:
        return
    
    # Detect if writer_instance is the wrapper or the core
    # If it has _core attribute, it's the wrapper; otherwise it's the core itself
    core = writer_instance._core if hasattr(writer_instance, '_core') else writer_instance
    
    # Add spacer before imported content
    core.content_buffer.append("\n\n")
    
    # Process content if conversion is enabled
    if convert_tables or fix_image_paths:
        # Split content into blocks (tables, images, text)
        lines = content.split('\n')
        i = 0
        current_block = []
        
        while i < len(lines):
            line = lines[i]
            
            # Detect markdown table
            if convert_tables and '|' in line and i + 1 < len(lines) and '|' in lines[i + 1]:
                # Save any accumulated text
                if current_block:
                    core.content_buffer.append('\n'.join(current_block) + '\n\n')
                    current_block = []
                
                # Extract table
                table_lines = [line]
                i += 1
                while i < len(lines) and ('|' in lines[i] or lines[i].strip() == ''):
                    if '|' in lines[i]:
                        table_lines.append(lines[i])
                    i += 1
                
                # Try to convert table to DataFrame
                try:
                    import pandas as pd
                    
                    # Parse markdown table
                    table_text = '\n'.join(table_lines)
                    print(f"DEBUG: Table detected with {len(table_lines)} lines")
                    for idx, tline in enumerate(table_lines):
                        print(f"  Line {idx}: {repr(tline)}")
                    
                    # Remove alignment row (e.g., |---|---|) - be more specific
                    rows = []
                    for r in table_lines:
                        # Skip lines that are only alignment characters
                        cleaned = r.replace('|', '').replace(' ', '').replace('\t', '')
                        if cleaned and not all(c in '-:' for c in cleaned):
                            rows.append(r)
                    
                    print(f"DEBUG: After filtering alignment rows: {len(rows)} rows")
                    for idx, row in enumerate(rows):
                        print(f"  Row {idx}: {repr(row)}")
                    
                    if len(rows) >= 2:  # At least header + 1 data row
                        # Parse table - handle tables with varying column counts
                        parsed_rows = []
                        for row in rows:
                            cells = [cell.strip() for cell in row.split('|')[1:-1]]
                            parsed_rows.append(cells)
                        
                        # Find maximum number of columns across all rows
                        max_cols = max(len(row) for row in parsed_rows)
                        
                        # Remember original header length before padding
                        original_header_cols = len(parsed_rows[0]) if parsed_rows else 0
                        
                        # Pad rows with fewer columns with empty strings
                        for row in parsed_rows:
                            while len(row) < max_cols:
                                row.append('')
                        
                        # Use first row as header, but if header has fewer columns than data,
                        # generate additional column names
                        header = parsed_rows[0]
                        if original_header_cols < max_cols:
                            # Replace empty padded columns with unnamed columns
                            for i in range(original_header_cols, max_cols):
                                header[i] = f'Unnamed_{i}'
                        
                        df = pd.DataFrame(parsed_rows[1:], columns=header)
                        print(f"DEBUG: DataFrame created successfully: {df.shape}")
                        print(f"DEBUG: Columns: {list(df.columns)}")
                        
                        # Look for caption in previous lines
                        caption = None
                        if i > len(table_lines):
                            for prev_line in reversed(lines[max(0, i - len(table_lines) - 5):i - len(table_lines)]):
                                if prev_line.strip().startswith(':') or 'Table' in prev_line or 'Tabla' in prev_line:
                                    caption = prev_line.strip().lstrip(':').strip()
                                    break
                        
                        # Add as styled table (show_figure=True to save as image with proper counter)
                        print(f"DEBUG: Adding table to document with caption: {caption}")
                        core.add_table(df, title=caption, show_figure=True)
                        print("DEBUG: Table added successfully - should be converted to image")
                        continue
                except Exception as e:
                    print(f"DEBUG: Exception during table parsing: {e}")
                    import traceback
                    traceback.print_exc()
                    # If parsing fails, add as raw markdown
                    core.content_buffer.append('\n'.join(table_lines) + '\n\n')
                    continue
            
            # Detect markdown image: ![alt](path)
            elif fix_image_paths and line.strip().startswith('!['):
                # Save any accumulated text
                if current_block:
                    core.content_buffer.append('\n'.join(current_block) + '\n\n')
                    current_block = []
                
                # Extract image
                match = re.match(r'!\[(.*?)\]\((.*?)\)(.*)$', line.strip())
                if match:
                    alt_text = match.group(1)
                    image_path = match.group(2)
                    attributes = match.group(3)  # Capture attributes like {#fig-esquema}
                    
                    # Store original path for markdown fallback
                    original_path = image_path
                    
                    # Fix path if relative - convert to absolute path
                    if not image_path.startswith('http') and not os.path.isabs(image_path):
                        base_dir = Path(file_path).parent
                        # Use resolve() to get absolute path
                        image_path = str((base_dir / image_path).resolve())
                    
                    # Look for caption in next line
                    caption = alt_text if alt_text else None
                    if i + 1 < len(lines) and lines[i + 1].strip().startswith(':'):
                        caption = lines[i + 1].strip().lstrip(':').strip()
                        i += 1
                    
                    # Add as figure if image exists
                    # Calculate width based on document columns to prevent overflow
                    if os.path.exists(image_path):
                        try:
                            # Get document type and layout from writer
                            document_type = getattr(core, 'document_type', 'report')
                            layout_style = getattr(core, 'layout_style', 'classic')
                            
                            # Calculate appropriate width spanning all columns
                            from ePy_docs.core._columns import calculate_content_width, get_width_string
                            from ePy_docs.core._config import load_layout
                            
                            try:
                                layout_config = load_layout(layout_style)
                                # Get default columns for this document type
                                default_columns = 1
                                if document_type in layout_config:
                                    columns_config = layout_config[document_type].get('columns', {})
                                    default_columns = columns_config.get('default', 1)
                                
                                # Calculate width spanning all columns
                                width_inches = calculate_content_width(
                                    document_type=document_type,
                                    layout_columns=default_columns,
                                    columns=default_columns  # Span full width
                                )
                                width_str = get_width_string(width_inches)
                            except Exception:
                                # Fallback to safe default (6.5in fits most standard pages)
                                width_str = '6.5in'
                            
                            core.add_image(image_path, caption=caption, width=width_str)
                            i += 1
                            continue
                        except Exception:
                            pass
                    
                    # If image doesn't exist or fails, add as raw markdown with CORRECTED path
                    # Convert path to forward slashes for LaTeX compatibility
                    corrected_path = image_path.replace('\\', '/')
                    corrected_line = f'![{alt_text}]({corrected_path}){attributes}'
                    core.content_buffer.append(corrected_line + '\n')
                    i += 1
                    continue
                else:
                    current_block.append(line)
            
            else:
                current_block.append(line)
            
            i += 1
        
        # Add remaining text
        if current_block:
            core.content_buffer.append('\n'.join(current_block))
    else:
        # No conversion, add raw content
        core.content_buffer.append(content)
    
    # Add trailing spacer for next content
    core.content_buffer.append("\n\n")


def prepare_generation(writer_instance, output_filename: str = None):
    """
    Prepare content for generation.
    
    Args:
        writer_instance: DocumentWriter instance
        output_filename: Optional output filename
        
    Returns:
        Tuple of (content, title)
        
    Raises:
        ValueError: If buffer is empty
        RuntimeError: If document already generated
    """
    # Check if already generated
    if hasattr(writer_instance, '_is_generated') and writer_instance._is_generated:
        raise RuntimeError("Document has already been generated. Create a new writer instance.")
    
    # Get content from buffer (writers.py provides content_buffer directly)
    content = ''.join(writer_instance.content_buffer)
    
    # Validate content is not empty
    if not content or content.strip() == '':
        raise ValueError("Cannot generate document: buffer is empty. Add some content first.")
    
    # Get title from config or use default
    title = output_filename or "Document"
    if title.endswith('.qmd'):
        title = title[:-4]
    
    return content, title


def generate_documents(
    content: str,
    title: str,
    html: bool = True,
    pdf: bool = True,
    output_filename: str = None,
    layout_name: str = 'classic',
    output_dir: str = None,
    document_type: str = 'report',
    language: str = 'en'
) -> dict:
    """
    Generate documents using core modules.
    
    Args:
        content: Markdown content
        title: Document title
        html: Generate HTML
        pdf: Generate PDF
        output_filename: Output filename
        layout_name: Layout style
        output_dir: Output directory
        document_type: Document type
        language: Document language
        
    Returns:
        Dictionary with generated file paths
    """
    # Ensure output directory exists
    if output_dir is None:
        from ePy_docs.core._config import get_absolute_output_directories
        output_paths = get_absolute_output_directories()
        output_dir = str(output_paths['report'])
    
    # Set output filename
    if output_filename is None:
        output_filename = title
    
    # Remove extension if present
    if output_filename.endswith('.qmd'):
        output_filename = output_filename[:-4]
    
    # Build output path
    from pathlib import Path
    output_path = Path(output_dir) / f"{output_filename}.qmd"
    
    # Determine output formats
    output_formats = []
    if html:
        output_formats.append('html')
    if pdf:
        output_formats.append('pdf')
    
    # Generate using core module
    result_paths = create_and_render(
        output_path=output_path,
        content=content,
        title=title,
        layout_name=layout_name,
        document_type=document_type,
        output_formats=output_formats,
        language=language
    )
    
    return {
        'qmd': result_paths.get('qmd'),
        'pdf': result_paths.get('pdf') if pdf else None,
        'html': result_paths.get('html') if html else None
    }
