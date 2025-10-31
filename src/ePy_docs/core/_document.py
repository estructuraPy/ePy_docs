"""
Document Processing Module

Main orchestrator that:
- Identifies document type (qmd, md, docx)
- Distributes processing to appropriate modules
- Coordinates document generation workflow
"""

from typing import Dict, Any, Optional, List
from pathlib import Path


# =============================================================================
# DOCUMENT TYPE DETECTION
# =============================================================================

def detect_document_type(file_path: Path) -> str:
    """
    Detect document type from file extension.
    
    Args:
        file_path: Path to document file
        
    Returns:
        Document type: 'qmd', 'markdown', 'word', or 'unknown'
    """
    extension = file_path.suffix.lower()
    
    type_mapping = {
        '.qmd': 'qmd',
        '.md': 'markdown',
        '.markdown': 'markdown',
        '.docx': 'word',
        '.doc': 'word'
    }
    
    return type_mapping.get(extension, 'unknown')


# =============================================================================
# DOCUMENT PROCESSING ROUTER
# =============================================================================

def process_document(
    input_path: Path,
    output_dir: Path,
    layout_name: str = 'classic',
    document_type: str = 'article',
    output_formats: List[str] = ['pdf', 'html'],
    **kwargs
) -> Dict[str, Path]:
    """
    Main document processing function.
    Routes to appropriate processor based on input file type.
    
    Args:
        input_path: Path to input file (qmd, md, or docx)
        output_dir: Output directory for generated files
        layout_name: Layout to use
        document_type: Document type (article, report, book)
        output_formats: List of output formats to generate
        **kwargs: Additional options
        
    Returns:
        Dictionary mapping format names to output file paths
    """
    from ePy_docs.core._quarto import create_and_render
    from ePy_docs.core._markdown import convert_markdown_to_qmd, read_markdown_file
    from ePy_docs.core._word import convert_docx_to_qmd
    
    # Detect document type
    doc_type = detect_document_type(input_path)
    
    # Prepare output path for QMD
    output_dir.mkdir(parents=True, exist_ok=True)
    qmd_path = output_dir / f"{input_path.stem}.qmd"
    
    if doc_type == 'qmd':
        # Already QMD, just copy to output
        import shutil
        shutil.copy2(input_path, qmd_path)
        
        # Read content for rendering
        with open(qmd_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract title from frontmatter if present
        from ePy_docs.core._markdown import extract_frontmatter
        frontmatter, body = extract_frontmatter(content)
        title = frontmatter.get('title', input_path.stem) if frontmatter else input_path.stem
        
    elif doc_type == 'markdown':
        # Convert markdown to QMD
        from ePy_docs.core._quarto import generate_quarto_yaml
        
        # Read markdown content
        content = read_markdown_file(input_path)
        
        # Extract existing frontmatter
        from ePy_docs.core._markdown import extract_frontmatter
        frontmatter, body = extract_frontmatter(content)
        
        # Get title
        title = frontmatter.get('title', input_path.stem) if frontmatter else input_path.stem
        
        # Generate Quarto YAML
        yaml_config = generate_quarto_yaml(
            title=title,
            layout_name=layout_name,
            document_type=document_type,
            output_formats=output_formats,
            **kwargs
        )
        
        # Convert to QMD
        convert_markdown_to_qmd(
            md_path=input_path,
            output_path=qmd_path,
            add_yaml=True,
            yaml_config=yaml_config
        )
        
    elif doc_type == 'word':
        # Convert DOCX to QMD
        from ePy_docs.core._quarto import generate_quarto_yaml
        
        title = kwargs.get('title', input_path.stem.replace('_', ' ').title())
        
        # Generate Quarto YAML
        yaml_config = generate_quarto_yaml(
            title=title,
            layout_name=layout_name,
            document_type=document_type,
            output_formats=output_formats,
            **kwargs
        )
        
        # Convert to QMD
        convert_docx_to_qmd(
            docx_path=input_path,
            output_path=qmd_path,
            yaml_config=yaml_config
        )
        
    else:
        raise ValueError(
            f"Unsupported document type: {doc_type}\n"
            f"Supported types: qmd, markdown, word"
        )
    
    # Render to output formats
    from ePy_docs.core._quarto import render_qmd
    
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
# DOCUMENT GENERATION FROM CONTENT
# =============================================================================

def create_document_from_content(
    content: str,
    output_path: Path,
    title: str,
    layout_name: str = 'classic',
    document_type: str = 'article',
    output_formats: List[str] = ['pdf', 'html'],
    **kwargs
) -> Dict[str, Path]:
    """
    Create document from markdown content string.
    
    Args:
        content: Markdown content
        output_path: Path for output QMD file
        title: Document title
        layout_name: Layout to use
        document_type: Document type
        output_formats: Formats to generate
        **kwargs: Additional options
        
    Returns:
        Dictionary mapping format names to output paths
    """
    from ePy_docs.core._quarto import create_and_render
    
    return create_and_render(
        output_path=output_path,
        content=content,
        title=title,
        layout_name=layout_name,
        document_type=document_type,
        output_formats=output_formats,
        **kwargs
    )


# =============================================================================
# BATCH PROCESSING
# =============================================================================

def process_multiple_documents(
    input_dir: Path,
    output_dir: Path,
    pattern: str = '*.md',
    **kwargs
) -> Dict[str, Dict[str, Path]]:
    """
    Process multiple documents in a directory.
    
    Args:
        input_dir: Input directory containing documents
        output_dir: Output directory
        pattern: File pattern to match (e.g., '*.md', '*.qmd')
        **kwargs: Options passed to process_document
        
    Returns:
        Dictionary mapping input filenames to their output paths
    """
    results = {}
    
    for file_path in input_dir.glob(pattern):
        if file_path.is_file():
            try:
                file_results = process_document(
                    input_path=file_path,
                    output_dir=output_dir / file_path.stem,
                    **kwargs
                )
                results[file_path.name] = file_results
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
                results[file_path.name] = {'error': str(e)}
    
    return results


# =============================================================================
# DOCUMENT VALIDATION
# =============================================================================

def validate_input_file(file_path: Path) -> bool:
    """
    Validate input file exists and is of supported type.
    
    Args:
        file_path: Path to input file
        
    Returns:
        True if valid
        
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file type not supported
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Input file not found: {file_path}")
    
    doc_type = detect_document_type(file_path)
    
    if doc_type == 'unknown':
        raise ValueError(
            f"Unsupported file type: {file_path.suffix}\n"
            f"Supported types: .qmd, .md, .markdown, .docx"
        )
    
    return True
