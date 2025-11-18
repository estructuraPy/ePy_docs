"""
Quarto Integration Module

Handles:
- Quarto YAML generation
- QMD file creation
- Quarto rendering (qmd -> pdf/html)
- Format coordination
"""

from typing import Dict, List, Optional, Tuple, Union, TYPE_CHECKING, Any

if TYPE_CHECKING:
    import pandas as pd
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
    output_formats: List[str] = None,
    fonts_dir: Path = None,
    language: str = 'en',
    author: str = None,
    subtitle: str = None,
    date: str = None,
    bibliography_path: str = None,
    csl_path: str = None,
    crossref_chapters: bool = None,
    crossref_fig_labels: str = 'arabic',
    crossref_tbl_labels: str = 'arabic',
    crossref_eq_labels: str = 'arabic',
    echo: bool = False,
    warning: bool = False,
    message: bool = False,
    columns: int = None
) -> Dict[str, Any]:
    """
    Generate complete Quarto YAML frontmatter.
    
    Args:
        title: Document title
        layout_name: Layout name ('classic', 'modern', 'handwritten', etc.)
        document_type: Document type ('article', 'report', 'book')
        output_formats: List of output formats ('pdf', 'html', 'tex', 'docx')
        fonts_dir: Absolute path to fonts directory (for PDF font loading)
        language: Document language ('en', 'es', 'fr', etc.)
        author: Document author
        subtitle: Document subtitle
        date: Document date
        bibliography_path: Path to bibliography file (.bib)
        csl_path: Path to CSL style file (.csl)
        crossref_chapters: Enable chapter numbering (None = auto-detect from document_type)
        crossref_fig_labels: Figure label format
        crossref_tbl_labels: Table label format
        crossref_eq_labels: Equation label format
        echo: Show code in output
        warning: Show warnings in output
        message: Show messages in output
        columns: Number of columns for document layout
        
    Returns:
        Dictionary with Quarto YAML configuration
    """
    if output_formats is None:
        output_formats = ['pdf', 'html']
        
    from ePy_docs.core._pdf import get_pdf_config
    from ePy_docs.core._html import get_html_config
    from ePy_docs.core._config import get_document_type_config
    
    # Load document type configuration
    try:
        doc_type_config = get_document_type_config(document_type)
    except ValueError:
        doc_type_config = {}
    
    # Base metadata
    yaml_config = {
        'title': title,
        'author': author or 'Anonymous',
        'lang': language,
    }
    
    # Optional metadata
    if subtitle:
        yaml_config['subtitle'] = subtitle
    if date:
        yaml_config['date'] = date
    
    # Format configuration (build formats first, then apply document_type overrides)
    format_config = {}
    
    # IMPORTANT: Always include PDF config if columns > 1, even if PDF output not requested
    # This is needed for proper multi-column layout configuration (classoption: twocolumn)
    if 'pdf' in output_formats or (columns is not None and columns > 1):
        pdf_config = get_pdf_config(
            layout_name=layout_name,
            document_type=document_type,
            fonts_dir=fonts_dir,
            columns=columns
        )
        format_config['pdf'] = pdf_config
    
    if 'html' in output_formats:
        html_config = get_html_config(
            layout_name=layout_name,
            document_type=document_type
        )
        # Merge quarto_html from document_type
        if 'quarto_html' in doc_type_config:
            for key, value in doc_type_config['quarto_html'].items():
                quarto_key = key.replace('_', '-')
                html_config[quarto_key] = value
        format_config['html'] = html_config
    
    yaml_config['format'] = format_config
    
    # Apply quarto_common settings from document_type AFTER format configs
    # This ensures document_type settings (like toc: false) override format defaults
    if 'quarto_common' in doc_type_config:
        for key, value in doc_type_config['quarto_common'].items():
            # Convert keys from snake_case to kebab-case for Quarto
            quarto_key = key.replace('_', '-')
            yaml_config[quarto_key] = value
    
    # Apply quarto_common settings from layout AFTER document_type
    # This allows layouts to override document_type defaults
    from ePy_docs.core._config import get_loader
    try:
        loader = get_loader()
        if loader:
            layout_config = loader.load_layout(layout_name)
            if 'quarto_common' in layout_config:
                for key, value in layout_config['quarto_common'].items():
                    # Convert keys from snake_case to kebab-case for Quarto
                    quarto_key = key.replace('_', '-')
                    yaml_config[quarto_key] = value
    except:
        pass  # If layout doesn't exist or has no quarto_common, continue
    
    # Bibliography and CSL
    # If paths are provided, use them as-is (they should be relative filenames after copying)
    # No need to convert backslashes since they're just filenames now
    if bibliography_path:
        yaml_config['bibliography'] = bibliography_path
    if csl_path:
        yaml_config['csl'] = csl_path
    
    # Crossref configuration
    # Use crossref from document_type config if available, otherwise use defaults
    if 'crossref' in doc_type_config:
        yaml_config['crossref'] = doc_type_config['crossref'].copy()
        # Allow parameter overrides
        if crossref_chapters is not None:
            yaml_config['crossref']['chapters'] = crossref_chapters
        if crossref_fig_labels:
            yaml_config['crossref']['fig-labels'] = crossref_fig_labels
        if crossref_tbl_labels:
            yaml_config['crossref']['tbl-labels'] = crossref_tbl_labels
        if crossref_eq_labels:
            yaml_config['crossref']['eq-labels'] = crossref_eq_labels
    else:
        # Fallback to old behavior
        if crossref_chapters is None:
            chapters_enabled = True if document_type != 'report' else False
        else:
            chapters_enabled = crossref_chapters
        
        yaml_config['crossref'] = {
            'chapters': chapters_enabled,
            'fig-labels': crossref_fig_labels,
            'tbl-labels': crossref_tbl_labels,
            'eq-labels': crossref_eq_labels,
        }
    
    # Code execution settings
    # Use execution from document_type config if available
    if 'execution' in doc_type_config:
        yaml_config['execute'] = doc_type_config['execution'].copy()
        # Allow parameter overrides
        if echo is not False:  # Only override if explicitly set
            yaml_config['execute']['echo'] = echo
        if warning is not False:
            yaml_config['execute']['warning'] = warning
        if message is not False:
            yaml_config['execute']['message'] = message
    else:
        # Fallback to parameters
        yaml_config['execute'] = {
            'echo': echo,
            'warning': warning,
            'message': message,
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
        
        # Skip URLs
        if img_path.startswith(('http://', 'https://')):
            return match.group(0)
        
        # Skip data URLs or other special formats (but not Windows paths)
        if ':' in img_path:
            # Check if it's a Windows path (drive letter followed by colon)
            if not (len(img_path) > 1 and img_path[1] == ':'):
                return match.group(0)
        
        # If path is already absolute (Windows or Unix), just fix slashes
        if img_path.startswith('/') or (len(img_path) > 1 and img_path[1] == ':'):
            # Convert backslashes to forward slashes for LaTeX
            abs_path_str = img_path.replace('\\', '/')
            return f'![{alt_text}]({abs_path_str})'
        
        # Convert relative path to absolute
        candidate_path = (base_dir / img_path).resolve()
        
        # If the path doesn't exist, try going up directories to find the root
        if not candidate_path.exists():
            parent_candidate = (base_dir.parent / img_path).resolve()
            if parent_candidate.exists():
                candidate_path = parent_candidate
            else:
                grandparent_candidate = (base_dir.parent.parent / img_path).resolve()
                if grandparent_candidate.exists():
                    candidate_path = grandparent_candidate
                else:
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
    fix_image_paths: bool = False,
    layout_name: str = 'classic',
    document_type: str = 'article',
    columns: int = None
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
        document_type: Document type (report, paper, book, etc.)
        columns: Number of columns for document layout
        
    Returns:
        Path to created QMD file
    """
    import shutil
    
    # Ensure parent directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Copy custom fonts to output directory if needed for PDF
    # Returns absolute path to fonts directory
    fonts_dir = _copy_layout_fonts_to_output(layout_name, output_path.parent)
    
    # Update PDF config with fonts directory path if needed
    if 'format' in yaml_config and 'pdf' in yaml_config['format']:
        if fonts_dir and 'include-in-header' in yaml_config['format']['pdf']:
            # The fonts directory path is already embedded in the header during generation
            # No need to regenerate the entire config
            pass
    
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
        
        # Get format config (primary font) and text config (font_file_template)
        format_config = loader.load_external('format')
        text_config = loader.load_external('text')
        
        format_font_families = format_config.get('font_families', {})
        text_font_families = text_config.get('shared_defaults', {}).get('font_families', {})
        
        format_font_config = format_font_families.get(font_family, {})
        text_font_config = text_font_families.get(font_family, {})
        
        primary_font = format_font_config.get('primary', '')
        font_file_template = text_font_config.get('font_file_template', '')
        
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


def _copy_bibliography_files_to_output(
    bibliography_path: Optional[str],
    csl_path: Optional[str],
    output_dir: Path
) -> Tuple[Optional[str], Optional[str]]:
    """Copy bibliography and CSL files to output directory for Quarto rendering.
    
    Quarto expects these files to be in the same directory as the .qmd file or
    in a relative path accessible from that directory. This function copies the
    files and returns the relative paths to use in the YAML configuration.
    
    Args:
        bibliography_path: Path to bibliography file (.bib) - can be absolute or None
        csl_path: Path to CSL style file (.csl) - can be absolute or None
        output_dir: Output directory where .qmd file will be saved
        
    Returns:
        Tuple of (bibliography_relative_path, csl_relative_path)
        Returns None for paths that weren't provided or couldn't be copied
    """
    import shutil
    from pathlib import Path
    
    bib_relative = None
    csl_relative = None
    
    # Copy bibliography file if provided
    if bibliography_path:
        try:
            source_bib = Path(bibliography_path)
            if source_bib.exists():
                # Copy to output directory with same filename
                dest_bib = output_dir / source_bib.name
                shutil.copy2(source_bib, dest_bib)
                # Return just the filename (relative to .qmd location)
                bib_relative = source_bib.name
        except Exception as e:
            print(f"Warning: Failed to copy bibliography file: {e}")
    
    # Copy CSL file if provided
    if csl_path:
        try:
            source_csl = Path(csl_path)
            if source_csl.exists():
                # Copy to output directory with same filename
                dest_csl = output_dir / source_csl.name
                shutil.copy2(source_csl, dest_csl)
                # Return just the filename (relative to .qmd location)
                csl_relative = source_csl.name
        except Exception as e:
            print(f"Warning: Failed to copy CSL file: {e}")
    
    return bib_relative, csl_relative


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
        
        # For HTML, specify output filename to match the QMD base name
        if output_format == 'html':
            html_filename = qmd_path.with_suffix('.html').name
            cmd.extend(['--output', html_filename])
    
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
    output_formats: List[str] = None,
    language: str = 'en',
    bibliography_path: str = None,
    csl_path: str = None,
    columns: int = None
) -> Dict[str, Path]:
    """
    Complete workflow: create QMD and render to specified formats.
    
    Args:
        output_path: Path to save QMD file
        content: Markdown content
        title: Document title
        layout_name: Layout name
        document_type: Document type
        output_formats: List of formats to generate ('pdf', 'html', 'tex', 'docx', 'markdown')
        language: Document language
        bibliography_path: Path to bibliography file (.bib) - will be copied to output directory
        csl_path: Path to CSL style file (.csl) - will be copied to output directory
        columns: Number of columns for document layout
        
    Returns:
        Dictionary mapping format names to output file paths
    """
    if output_formats is None:
        output_formats = ['pdf', 'html']
    
    # Copy bibliography and CSL files to output directory (same location as .qmd)
    # This ensures Quarto can find them during rendering
    output_dir = output_path.parent
    bib_relative, csl_relative = _copy_bibliography_files_to_output(
        bibliography_path, csl_path, output_dir
    )
    
    # Generate YAML configuration with relative paths (just filenames)
    yaml_config = generate_quarto_yaml(
        title=title,
        layout_name=layout_name,
        document_type=document_type,
        output_formats=output_formats,
        language=language,
        bibliography_path=bib_relative,  # Use relative path (just filename)
        csl_path=csl_relative,           # Use relative path (just filename)
        columns=columns
    )
    
    # Create QMD file with CSS generation
    # Don't fix image paths since our tables already generate correct relative paths
    qmd_path = create_qmd_file(output_path, content, yaml_config, fix_image_paths=False, 
                               layout_name=layout_name, document_type=document_type, columns=columns)
    
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
def _is_table_start(line: str, lines: list, index: int) -> bool:
    """Check if current line starts a markdown table."""
    return ('|' in line and 
            index + 1 < len(lines) and 
            '|' in lines[index + 1])


def _extract_table_content(lines: list, start_index: int) -> Tuple[List[str], Optional[str], int]:
    """Extract table lines and caption from markdown.
    
    Returns:
        Tuple of (table_lines, caption, next_index)
    """
    table_lines = [lines[start_index]]
    i = start_index + 1
    table_caption = None
    
    while i < len(lines):
        current_line = lines[i].strip()
        
        if '|' in lines[i]:
            table_lines.append(lines[i])
        elif current_line == '':
            # Skip empty lines within table
            pass
        elif current_line.startswith(':') and table_caption is None:
            # Quarto table caption
            table_caption = current_line[1:].strip()
            i += 1  # Move past caption line
            break
        else:
            # End of table reached
            break
        i += 1
    
    return table_lines, table_caption, i


def _process_image_line(line: str, file_path: str, core) -> bool:
    """Process a markdown image line and add to core if valid.
    
    Returns:
        True if image was processed successfully, False otherwise
    """
    import re
    import os
    from pathlib import Path
    
    match = re.match(r'!\[(.*?)\]\((.*?)\)', line.strip())
    if not match:
        return False
        
    alt_text = match.group(1)
    image_path = match.group(2)
    
    # Fix relative paths
    if not image_path.startswith('http') and not os.path.isabs(image_path):
        base_dir = Path(file_path).parent
        image_path = str((base_dir / image_path).resolve())
    
    # Add image if it exists
    if os.path.exists(image_path):
        caption = alt_text if alt_text else None
        try:
            core.add_image(image_path, caption=caption, width='6.5in')
            return True
        except Exception:
            return False
    
    return False


def _parse_markdown_table(table_lines: list) -> 'pd.DataFrame':
    """Parse markdown table lines into a pandas DataFrame.
    
    Args:
        table_lines: List of markdown table lines
        
    Returns:
        DataFrame if parsing succeeds, None otherwise
    """
    try:
        import pandas as pd
        
        # Filter out alignment rows and empty lines
        valid_rows = []
        for line in table_lines:
            line = line.strip()
            if not line:
                continue
            # Skip alignment rows (contain only |, -, :, spaces)  
            cleaned = line.replace('|', '').replace(' ', '').replace('\t', '')
            if cleaned and not all(c in '-:' for c in cleaned):
                valid_rows.append(line)
        
        if len(valid_rows) < 2:  # Need at least header + 1 data row
            return None
            
        # Parse rows into cells
        parsed_rows = []
        for row in valid_rows[:20]:  # Limit rows to prevent performance issues
            cells = [cell.strip() for cell in row.split('|')[1:-1]]
            if cells:
                parsed_rows.append(cells)
        
        if len(parsed_rows) < 2:
            return None
            
        # Create DataFrame
        header = parsed_rows[0]
        data_rows = parsed_rows[1:]
        
        # Normalize row lengths
        max_cols = len(header)
        for row in data_rows:
            # Pad short rows
            while len(row) < max_cols:
                row.append('')
            # Truncate long rows
            if len(row) > max_cols:
                row[:] = row[:max_cols]
        
        return pd.DataFrame(data_rows, columns=header)
        
    except Exception:
        return None


def process_quarto_file(
    file_path: str,
    include_yaml: bool = False,
    fix_image_paths: bool = True,
    convert_tables: bool = True,
    output_dir: str = None,
    figure_counter: int = 1,
    document_type: str = 'report',
    writer_instance = None,
    execute_code_blocks: bool = True
) -> None:
    """
    Process Quarto file and add to writer.
    
    Automatically processes:
    - Markdown tables: Converts to styled image tables
    - Images: Extracts caption from markdown and adds as figure
    - Text content: Preserves as-is
    - YAML frontmatter: Optionally included or stripped
    - Code blocks: Optionally executed if execute_code_blocks=True
    
    Args:
        file_path: Path to Quarto file
        include_yaml: Whether to include YAML frontmatter
        fix_image_paths: Whether to fix image paths
        convert_tables: Whether to convert tables to styled images
        output_dir: Output directory
        figure_counter: Current figure counter
        document_type: Document type
        writer_instance: DocumentWriter instance
        execute_code_blocks: Whether to execute code blocks (default True)
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
    
    # Clean Quarto-specific syntax that might cause issues
    # Remove cross-references (@fig-xxx, @tbl-xxx, etc.)
    import re
    content = re.sub(r'@fig-[\w-]+', '[Figure]', content)
    content = re.sub(r'@tbl-[\w-]+', '[Table]', content)
    content = re.sub(r'@eq-[\w-]+', '[Equation]', content)
    
    # Clean complex figure blocks and convert to simple images
    content = re.sub(r'::: \{[^}]*#fig-[^}]*\}.*?:::', '', content, flags=re.DOTALL)
    
    # Clean image attributes that might cause issues
    content = re.sub(r'\{#[\w-]+[^}]*\}', '', content)
    
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
            if convert_tables and _is_table_start(line, lines, i):
                # Save any accumulated text
                if current_block:
                    core.content_buffer.append('\n'.join(current_block) + '\n\n')
                    current_block = []
                
                # Extract table content and caption
                table_lines, table_caption, i = _extract_table_content(lines, i)
                
                # Convert markdown table to DataFrame
                df = _parse_markdown_table(table_lines)
                if df is not None:
                    # Add table with proper caption
                    core.add_table(df, title=table_caption, show_figure=True)
                    continue
                else:
                    # Failed to parse - add as raw markdown
                    core.content_buffer.append('\n'.join(table_lines) + '\n\n')
                    continue
            
            # Detect markdown image: ![alt](path)
            elif fix_image_paths and line.strip().startswith('!['):
                # Save any accumulated text
                if current_block:
                    core.content_buffer.append('\n'.join(current_block) + '\n\n')
                    current_block = []
                
                # Process image - if successful, skip raw markdown
                if not _process_image_line(line, file_path, core):
                    # Image processing failed, add as raw markdown
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
    """
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

# ============================================================================
# COMPATIBILITY LAYER FOR TESTS
# ============================================================================

class QuartoOrchestrator:
    """Compatibility wrapper for tests that expect quarto_orchestrator singleton."""
    
    def generate_yaml_config(self, 
                            title: str,
                            layout_name: str = 'classic',
                            document_type: str = 'article',
                            output_formats = None,
                            language: str = 'en',
                            **kwargs):
        """Generate Quarto YAML configuration."""
        return generate_quarto_yaml(
            title=title,
            layout_name=layout_name,
            document_type=document_type,
            output_formats=output_formats,
            language=language,
            **kwargs
        )


# Singleton instance for tests
quarto_orchestrator = QuartoOrchestrator()
