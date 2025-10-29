"""Path utilities for ePy_docs.

Handles output directory resolution and path management.
"""

from pathlib import Path
from typing import Dict
import os


def get_caller_directory() -> Path:
    """Get the directory of the script/notebook that called the library.
    
    Uses the call stack to find the first frame outside of ePy_docs package.
    This allows automatic detection of the user's working directory.
    
    Returns:
        Path to the directory containing the calling script/notebook
    """
    import inspect
    
    # Get current frame stack
    frame_stack = inspect.stack()
    
    # Find the first frame that's not from ePy_docs package
    for frame_info in frame_stack:
        frame_file = Path(frame_info.filename)
        
        # Skip frames from ePy_docs package
        if 'ePy_docs' not in str(frame_file):
            # Return directory of the calling file
            if frame_file.name == '<stdin>' or frame_file.name.startswith('<ipython'):
                # Jupyter notebook or interactive session - use current directory
                return Path.cwd()
            else:
                # Regular Python script - use script's directory
                return frame_file.parent
    
    # Fallback to current directory if no external caller found
    return Path.cwd()


def get_absolute_output_directories(document_type: str = "report") -> Dict[str, str]:
    """Get absolute paths for output directories.
    
    Args:
        document_type: Type of document ("report" or "paper") to determine correct paths
        
    Returns:
        Dictionary with absolute paths for different output directories
    """
    # Simple relative paths matching project structure
    # Select correct tables/figures directories based on document type
    base_path = Path.cwd()
    
    if document_type == "paper":
        tables_dir = Path('results') / 'paper' / 'tables'
        figures_dir = Path('results') / 'paper' / 'figures'
        output_dir = Path('results') / 'paper'
    else:  # document_type == "report" or fallback
        tables_dir = Path('results') / 'report' / 'tables'
        figures_dir = Path('results') / 'report' / 'figures'
        output_dir = Path('results') / 'report'
    
    return {
        'data': str(base_path / 'data'),
        'results': str(base_path / 'results'),
        'configuration': str(base_path / 'data' / 'configuration'),
        'brand': str(base_path / 'data' / 'user' / 'brand'),
        'templates': str(base_path / 'data' / 'user' / 'templates'),
        'user': str(base_path / 'data' / 'user'),
        'report': str(base_path / 'results' / 'report'),
        'paper': str(base_path / 'results' / 'paper'),
        'examples': str(base_path / 'data' / 'examples'),
        # Document-specific directories (active based on document_type)
        'tables': str(base_path / tables_dir),
        'figures': str(base_path / figures_dir),
        'output': str(base_path / output_dir),
        # All specific table and figure directories (for direct access)
        'tables_report': str(base_path / 'results' / 'report' / 'tables'),
        'figures_report': str(base_path / 'results' / 'report' / 'figures'),
        'tables_paper': str(base_path / 'results' / 'paper' / 'tables'),
        'figures_paper': str(base_path / 'results' / 'paper' / 'figures')
    }
