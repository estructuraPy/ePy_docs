"""
Configuration Path Utilities

Utilities for path resolution and output directory management.
"""

import inspect
from pathlib import Path
from typing import Dict


def get_caller_directory() -> Path:
    """Get the directory of the script/notebook that called the library."""
    frame_stack = inspect.stack()
    
    for frame_info in frame_stack:
        frame_file = Path(frame_info.filename)
        
        if 'ePy_docs' not in str(frame_file):
            if frame_file.name == '<stdin>' or frame_file.name.startswith('<ipython'):
                return Path.cwd()
            else:
                return frame_file.parent
    
    return Path.cwd()


def get_absolute_output_directories(document_type: str = "report") -> Dict[str, str]:
    """Get absolute paths for output directories.
    
    Args:
        document_type: Type of document (must exist in documents.epyson)
        
    Raises:
        ValueError: If document_type not found or configuration invalid
    """
    from ._config import ModularConfigLoader
    
    base_path = Path.cwd()
    
    # Load document configuration from individual file
    config_loader = ModularConfigLoader()
    
    # Try to load from documents/{type}.epyson
    try:
        type_config = config_loader.load_external(f'documents.{document_type}')
    except FileNotFoundError:
        # List available document types
        documents_dir = config_loader.config_dir / 'documents'
        available_types = [f.stem for f in documents_dir.glob('*.epyson')] if documents_dir.exists() else []
        available = ', '.join(available_types) if available_types else 'none'
        raise ValueError(f"Document type '{document_type}' not found. Available: {available}")
    
    # Validate required fields
    if 'output_dir' not in type_config:
        raise ValueError(f"Missing 'output_dir' in configuration for document type '{document_type}'")
    
    output_dir_name = type_config['output_dir']
    
    tables_dir = Path('results') / output_dir_name / 'tables'
    figures_dir = Path('results') / output_dir_name / 'figures'
    output_dir = Path('results') / output_dir_name
    
    # Build base directories that all document types need
    base_directories = {
        'data': str(base_path / 'data'),
        'results': str(base_path / 'results'),
        'configuration': str(base_path / 'data' / 'configuration'),
        'brand': str(base_path / 'data' / 'user' / 'brand'),
        'templates': str(base_path / 'data' / 'user' / 'templates'),
        'user': str(base_path / 'data' / 'user'),
        'examples': str(base_path / 'data' / 'examples'),
        'tables': str(base_path / tables_dir),
        'figures': str(base_path / figures_dir),
        'output': str(base_path / output_dir),
    }
    
    # Load all available document types for dynamic directories
    documents_dir = config_loader.config_dir / 'documents'
    if documents_dir.exists():
        for doc_file in documents_dir.glob('*.epyson'):
            doc_name = doc_file.stem
            try:
                doc_config = config_loader.load_external(f'documents.{doc_name}')
                dir_name = doc_config.get('output_dir', doc_name)
                base_directories[doc_name] = str(base_path / 'results' / dir_name)
                base_directories[f'tables_{doc_name}'] = str(base_path / 'results' / dir_name / 'tables')
                base_directories[f'figures_{doc_name}'] = str(base_path / 'results' / dir_name / 'figures')
            except Exception:
                # Skip documents that can't be loaded
                continue
    
    return base_directories
