"""
Writer Initialization Logic
===========================

Handles all initialization logic for DocumentWriter.
This module contains the business logic that was previously in writers.py __init__.
"""

import os


def validate_and_setup_writer(document_type: str, layout_style: str = None):
    """
    Validate document type and setup initial configuration.
    
    Args:
        document_type: Type of document to create
        layout_style: Optional layout style
        
    Returns:
        tuple: (validated_document_type, final_layout_style, output_dir, config_dict)
        
    Raises:
        ValueError: If document_type is invalid
    """
    # Validate document type
    valid_types = ["report", "paper"]
    if document_type not in valid_types:
        raise ValueError(
            f"document_type must be one of {valid_types}, got '{document_type}'"
        )
    
    # Set default layout_style based on document_type if not provided
    if layout_style is None:
        layout_style = "classic" if document_type == "report" else "academic"
    
    # Setup output directory
    output_dir = _setup_output_directory(document_type)
    
    # Create legacy compatibility config
    config = {"layouts": {layout_style: {"name": document_type.title()}}}
    
    return document_type, layout_style, output_dir, config


def _setup_output_directory(document_type: str) -> str:
    """
    Setup output directory for the document.
    
    Args:
        document_type: Type of document
        
    Returns:
        str: Path to output directory
    """
    try:
        from ePy_docs.config.setup import get_absolute_output_directories
        output_dirs = get_absolute_output_directories(document_type=document_type)
        output_dir = output_dirs.get('output')
    except Exception:
        # Fallback to default directory
        output_dir = os.path.join(os.getcwd(), 'results', document_type)
        os.makedirs(output_dir, exist_ok=True)
    
    return output_dir
