"""
Word Document Processing Module

Handles:
- DOCX file reading
- Content extraction from Word documents
- Conversion to markdown/QMD format
"""

from typing import Dict, Any, Optional, List
from pathlib import Path


# =============================================================================
# WORD DOCUMENT READING
# =============================================================================

def read_docx_file(file_path: Path) -> str:
    """
    Read content from Word document (.docx).
    
    Args:
        file_path: Path to DOCX file
        
    Returns:
        Extracted text content
        
    Raises:
        FileNotFoundError: If file doesn't exist
        ImportError: If python-docx not installed
    """
    if not file_path.exists():
        raise FileNotFoundError(f"DOCX file not found: {file_path}")
    
    try:
        from docx import Document
    except ImportError:
        raise ImportError(
            "python-docx library required for Word document processing.\n"
            "Install with: pip install python-docx"
        )
    
    doc = Document(file_path)
    
    # Extract all paragraph text
    paragraphs = [paragraph.text for paragraph in doc.paragraphs]
    content = '\n\n'.join(paragraphs)
    
    return content


# =============================================================================
# CONTENT EXTRACTION
# =============================================================================

def extract_paragraphs(file_path: Path) -> List[str]:
    """
    Extract paragraphs from Word document.
    
    Args:
        file_path: Path to DOCX file
        
    Returns:
        List of paragraph texts
    """
    try:
        from docx import Document
    except ImportError:
        raise ImportError("python-docx library required")
    
    doc = Document(file_path)
    return [p.text for p in doc.paragraphs if p.text.strip()]


def extract_tables(file_path: Path) -> List[List[List[str]]]:
    """
    Extract tables from Word document.
    
    Args:
        file_path: Path to DOCX file
        
    Returns:
        List of tables, each table is a list of rows, each row is a list of cell values
    """
    try:
        from docx import Document
    except ImportError:
        raise ImportError("python-docx library required")
    
    doc = Document(file_path)
    tables = []
    
    for table in doc.tables:
        table_data = []
        for row in table.rows:
            row_data = [cell.text for cell in row.cells]
            table_data.append(row_data)
        tables.append(table_data)
    
    return tables


def extract_headings(file_path: Path) -> List[Dict[str, Any]]:
    """
    Extract headings from Word document.
    
    Args:
        file_path: Path to DOCX file
        
    Returns:
        List of headings with {'level': int, 'text': str}
    """
    try:
        from docx import Document
    except ImportError:
        raise ImportError("python-docx library required")
    
    doc = Document(file_path)
    headings = []
    
    for paragraph in doc.paragraphs:
        if paragraph.style.name.startswith('Heading'):
            try:
                level = int(paragraph.style.name.replace('Heading ', ''))
                headings.append({
                    'level': level,
                    'text': paragraph.text
                })
            except ValueError:
                continue
    
    return headings


# =============================================================================
# CONVERSION TO MARKDOWN
# =============================================================================

def convert_docx_to_markdown(file_path: Path) -> str:
    """
    Convert Word document to markdown format.
    
    Args:
        file_path: Path to DOCX file
        
    Returns:
        Markdown content
    """
    try:
        from docx import Document
    except ImportError:
        raise ImportError("python-docx library required")
    
    doc = Document(file_path)
    markdown_lines = []
    
    for paragraph in doc.paragraphs:
        text = paragraph.text.strip()
        
        if not text:
            markdown_lines.append('')
            continue
        
        # Convert headings
        if paragraph.style.name.startswith('Heading'):
            try:
                level = int(paragraph.style.name.replace('Heading ', ''))
                markdown_lines.append(f"{'#' * level} {text}")
            except ValueError:
                markdown_lines.append(text)
        else:
            # Regular paragraph
            markdown_lines.append(text)
        
        markdown_lines.append('')
    
    return '\n'.join(markdown_lines)


def convert_docx_to_qmd(
    docx_path: Path,
    output_path: Path,
    yaml_config: Optional[Dict[str, Any]] = None
) -> Path:
    """
    Convert Word document to Quarto QMD file.
    
    Args:
        docx_path: Path to input DOCX file
        output_path: Path to output QMD file
        yaml_config: Optional YAML configuration
        
    Returns:
        Path to created QMD file
    """
    import yaml
    
    # Convert to markdown
    markdown_content = convert_docx_to_markdown(docx_path)
    
    # Add YAML frontmatter
    if yaml_config is None:
        yaml_config = {
            'title': docx_path.stem.replace('_', ' ').title()
        }
    
    yaml_str = yaml.dump(yaml_config, default_flow_style=False, sort_keys=False)
    
    qmd_content = f'''---
{yaml_str}---

{markdown_content}
'''
    
    # Write to file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(qmd_content)
    
    return output_path


# =============================================================================
# UTILITIES
# =============================================================================

def validate_docx_file(file_path: Path) -> bool:
    """
    Validate that file is a Word document.
    
    Args:
        file_path: Path to file
        
    Returns:
        True if valid DOCX file
        
    Raises:
        ValueError: If not a DOCX file
    """
    if file_path.suffix.lower() != '.docx':
        raise ValueError(
            f"Not a Word document: {file_path}\n"
            f"Expected .docx file"
        )
    
    return True


def is_docx_available() -> bool:
    """
    Check if python-docx library is available.
    
    Returns:
        True if python-docx is installed
    """
    try:
        import docx
        return True
    except ImportError:
        return False
