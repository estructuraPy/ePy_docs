"""
File Processing with Table Conversion
======================================

Handles processing of Markdown and Quarto files with automatic table conversion.
This module contains all the business logic for file processing.
"""

from ePy_docs.internals.delegation._common import (
    os, tempfile, List, Tuple, Any,
    process_markdown_file, process_quarto_file,
    extract_markdown_tables, remove_tables_from_content
)


def process_markdown_with_tables(
    file_path: str,
    fix_image_paths: bool,
    convert_tables: bool,
    output_dir: str,
    figure_counter: int,
    writer_instance
) -> None:
    """
    Process a Markdown file with optional table conversion.
    
    This function handles:
    1. Reading the file
    2. Extracting Markdown tables
    3. Removing tables from content
    4. Processing content
    5. Interleaving processed content with styled tables
    
    Args:
        file_path: Path to the .md file
        fix_image_paths: Whether to fix image paths
        convert_tables: Whether to convert MD tables to styled tables
        output_dir: Output directory for generated files
        figure_counter: Current figure counter
        writer_instance: DocumentWriter instance to call methods on
    """
    
    # Read the file
    with open(file_path, 'r', encoding='utf-8') as f:
        original_content = f.read()
    
    if not convert_tables:
        # Simple path: no table conversion
        content, new_counter = process_markdown_file(
            file_path=file_path,
            fix_image_paths=fix_image_paths,
            output_dir=output_dir,
            figure_counter=figure_counter
        )
        writer_instance.add_content(content)
        writer_instance.figure_counter = new_counter
        return
    
    # Complex path: extract and convert tables
    tables_info = extract_markdown_tables(original_content)
    
    if not tables_info:
        # No tables found, process normally
        content, new_counter = process_markdown_file(
            file_path=file_path,
            fix_image_paths=fix_image_paths,
            output_dir=output_dir,
            figure_counter=figure_counter
        )
        writer_instance.add_content(content)
        writer_instance.figure_counter = new_counter
        return
    
    # Remove tables from content
    content_without_tables = remove_tables_from_content(original_content, tables_info)
    
    # Save to temporary file
    with tempfile.NamedTemporaryFile(
        mode='w', suffix='.md', delete=False, encoding='utf-8'
    ) as tmp:
        tmp.write(content_without_tables)
        tmp_path = tmp.name
    
    try:
        # Process content without tables
        content, new_counter = process_markdown_file(
            file_path=tmp_path,
            fix_image_paths=fix_image_paths,
            output_dir=output_dir,
            figure_counter=figure_counter
        )
        writer_instance.figure_counter = new_counter
        
        # Build table map
        table_map = {
            f"<!-- TABLE_PLACEHOLDER_{start_line} -->": (df, caption)
            for df, caption, start_line, _ in tables_info
        }
        
        # Interleave content and tables
        _interleave_content_and_tables(content, table_map, writer_instance)
        
    finally:
        # Clean up temporary file
        os.unlink(tmp_path)


def process_quarto_with_tables(
    file_path: str,
    include_yaml: bool,
    fix_image_paths: bool,
    convert_tables: bool,
    output_dir: str,
    figure_counter: int,
    document_type: str,
    writer_instance
) -> None:
    """
    Process a Quarto file with optional table conversion.
    
    Args:
        file_path: Path to the .qmd file
        include_yaml: Whether to include YAML frontmatter
        fix_image_paths: Whether to fix image paths
        convert_tables: Whether to convert MD tables to styled tables
        output_dir: Output directory for generated files
        figure_counter: Current figure counter
        document_type: Type of document (report/paper)
        writer_instance: DocumentWriter instance to call methods on
    """
    
    # Read the file
    with open(file_path, 'r', encoding='utf-8') as f:
        original_content = f.read()
    
    if not convert_tables:
        # Simple path: no table conversion
        content, new_counter = process_quarto_file(
            file_path=file_path,
            include_yaml=include_yaml,
            fix_image_paths=fix_image_paths,
            output_dir=output_dir,
            figure_counter=figure_counter,
            document_type=document_type
        )
        writer_instance.add_content(content)
        writer_instance.figure_counter = new_counter
        return
    
    # Complex path: extract and convert tables
    tables_info = extract_markdown_tables(original_content)
    
    if not tables_info:
        # No tables found, process normally
        content, new_counter = process_quarto_file(
            file_path=file_path,
            include_yaml=include_yaml,
            fix_image_paths=fix_image_paths,
            output_dir=output_dir,
            figure_counter=figure_counter,
            document_type=document_type
        )
        writer_instance.add_content(content)
        writer_instance.figure_counter = new_counter
        return
    
    # Remove tables from content
    content_without_tables = remove_tables_from_content(original_content, tables_info)
    
    # Save to temporary file
    with tempfile.NamedTemporaryFile(
        mode='w', suffix='.qmd', delete=False, encoding='utf-8'
    ) as tmp:
        tmp.write(content_without_tables)
        tmp_path = tmp.name
    
    try:
        # Process content without tables
        content, new_counter = process_quarto_file(
            file_path=tmp_path,
            include_yaml=include_yaml,
            fix_image_paths=fix_image_paths,
            output_dir=output_dir,
            figure_counter=figure_counter,
            document_type=document_type
        )
        writer_instance.figure_counter = new_counter
        
        # Build table map
        table_map = {
            f"<!-- TABLE_PLACEHOLDER_{start_line} -->": (df, caption)
            for df, caption, start_line, _ in tables_info
        }
        
        # Interleave content and tables
        _interleave_content_and_tables(content, table_map, writer_instance)
        
    finally:
        # Clean up temporary file
        os.unlink(tmp_path)


def _interleave_content_and_tables(content: str, table_map: dict, writer_instance) -> None:
    """
    Interleave processed content with styled tables.
    
    Args:
        content: Processed content with placeholders
        table_map: Map of placeholders to (df, caption) tuples
        writer_instance: DocumentWriter instance to call add_table on
    """
    lines = content.split('\n')
    buffer = []
    
    for line in lines:
        if line.strip() in table_map:
            # Add accumulated buffer
            if buffer:
                writer_instance.add_content('\n'.join(buffer))
                buffer = []
            # Add the table
            df, caption = table_map[line.strip()]
            writer_instance.add_table(df, title=caption)
        else:
            buffer.append(line)
    
    # Add remaining content
    if buffer:
        writer_instance.add_content('\n'.join(buffer))
