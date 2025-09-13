"""
Reference and citation formatting for ePy_docs.

This module provides functionality to format cross-references 
and citations in documentation.
"""

from typing import Optional, Dict, Any
from pathlib import Path


def format_cross_reference(ref_type: str, ref_id: str, custom_text: Optional[str] = None) -> str:
    """Format cross-reference to figure, table, equation, or note.
    
    Args:
        ref_type: Type of reference ('fig', 'tbl', 'eq', 'note')
        ref_id: Reference ID
        custom_text: Optional custom text for the reference
        
    Returns:
        Formatted cross-reference
        
    Raises:
        ValueError: If ref_type is invalid
    """
    if ref_type == 'note':
        # Note references are handled by the note renderer
        # This will be handled in the calling method
        return ""
    elif ref_type in ['fig', 'tbl', 'eq']:
        if custom_text:
            return f"[{custom_text}](#{ref_id})"
        else:
            return f"@{ref_id}"
    else:
        raise ValueError(f"Invalid reference type: {ref_type}")


def format_citation(citation_key: str, page: Optional[str] = None) -> str:
    """Format inline citation.
    
    Args:
        citation_key: Citation key from bibliography
        page: Optional page number
        
    Returns:
        Formatted citation
    """
    if page:
        return f"[@{citation_key}, p. {page}]"
    else:
        return f"[@{citation_key}]"


def get_default_citation_style(layout_name: str = None) -> str:
    """Get default citation style from layout configuration.
    
    Args:
        layout_name: Name of the layout (if None, uses global current layout)
        
    Returns:
        str: Citation style name from layout configuration, fallback to 'ieee'
    """
    try:
        # Import here to avoid circular imports
        from ePy_docs.components.pages import get_layout_config
        
        # Use get_layout_config which reads from report.json
        layout_config = get_layout_config(layout_name)
        
        if 'citation_style' not in layout_config:
            # Fallback to ieee if layout doesn't specify citation_style
            return 'ieee'
        
        return layout_config['citation_style']
    except Exception:
        # Fallback to ieee if there are any configuration issues
        return 'ieee'


def get_bibliography_config(config=None, sync_files: bool = None) -> Dict[str, Any]:
    """Get bibliography configuration using setup.json paths.
    
    Args:
        config: Configuration object (optional)
        sync_files: Whether to sync files (if None, uses project setting)
    
    Returns:
        Dict with 'bibliography' and 'csl' paths.
        
    Raises:
        ConfigurationError: If configuration is missing or files don't exist.
    """
    from ePy_docs.files import _load_cached_files
    from ePy_docs.components.setup import _resolve_config_path, get_absolute_output_directories, get_current_project_config
    from ePy_docs.components.pages import ConfigurationError
    
    # Determine sync_files setting if not provided
    if sync_files is None:
        current_config = get_current_project_config()
        sync_files = current_config.settings.sync_files if current_config else True
    
    # Load setup configuration using the correct pattern
    setup_config_path = _resolve_config_path('components/setup', sync_files)
    setup_config = _load_cached_files(setup_config_path, sync_files)
    output_dirs = get_absolute_output_directories(document_type="report")
    config_dir = output_dirs['configuration']
    
    # Use local configuration folder - references are in components
    ref_dir = Path(config_dir) / "components"
    bib_file = ref_dir / "references.bib"
    csl_file = ref_dir / f"{get_default_citation_style()}.csl"
    
    # Source files in components directory (relative to this file)
    src_components_dir = Path(__file__).parent
    src_bib_file = src_components_dir / "references.bib"
    src_csl_file = src_components_dir / f"{get_default_citation_style()}.csl"
    
    # Choose appropriate files based on sync_files and file existence
    final_bib_file = bib_file if bib_file.exists() else src_bib_file
    final_csl_file = csl_file if csl_file.exists() else src_csl_file
    
    if not final_bib_file.exists():
        raise ConfigurationError(f"Bibliography file not found: {final_bib_file}")
    if not final_csl_file.exists():
        raise ConfigurationError(f"Citation style file not found: {final_csl_file}")
        
    return {
        'bibliography': str(final_bib_file.absolute()),
        'csl': str(final_csl_file.absolute())
    }
