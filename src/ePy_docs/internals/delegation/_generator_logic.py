"""
Document Generation Logic
=========================

Handles all business logic for document generation.
This module contains validation and configuration logic for generation.
"""


def prepare_generation(
    writer_instance,
    output_filename: str = None
) -> tuple:
    """
    Prepare for document generation.
    
    Validates preconditions and prepares configuration.
    
    Args:
        writer_instance: DocumentWriter instance
        output_filename: Optional output filename
        
    Returns:
        tuple: (content, project_title)
        
    Raises:
        RuntimeError: If document already generated
        ValueError: If buffer is empty
    """
    # Validate preconditions
    if writer_instance._is_generated:
        raise RuntimeError(
            "Document has already been generated. "
            "Create a new writer instance to generate another document."
        )
    
    content = writer_instance.get_content()
    if not content or content.strip() == "":
        raise ValueError(
            "Cannot generate document: buffer is empty. "
            "Add content before calling generate()."
        )
    
    # Get project title
    if output_filename:
        project_title = output_filename
    else:
        project_title = _get_document_title_from_config(
            writer_instance.document_type,
            writer_instance.layout_style
        )
    
    return content, project_title


def _get_document_title_from_config(document_type: str, layout_style: str) -> str:
    """
    Get document title from configuration.
    
    Args:
        document_type: Type of document
        layout_style: Layout style name
        
    Returns:
        str: Document title
    """
    try:
        from ePy_docs.internals.data_processing._data import load_cached_files
        from ePy_docs.config.setup import _resolve_config_path
        
        config = load_cached_files(
            _resolve_config_path(f'components/{document_type}')
        )
        doc_name = (
            config.get('layouts', {})
            .get(layout_style, {})
            .get(f'{document_type}_name')
        )
        
        return doc_name if doc_name else document_type.title()
    except Exception:
        # Fallback to document type title
        return document_type.title()
