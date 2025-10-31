"""
References and Bibliography Module

Handles:
- Citation management
- Bibliography generation
- CSL style configuration
- BibTeX integration
"""

from typing import Dict, Any, List, Optional
from pathlib import Path
import shutil


# =============================================================================
# CSL STYLES
# =============================================================================

AVAILABLE_CSL_STYLES = {
    'ieee': {
        'name': 'IEEE',
        'description': 'Institute of Electrical and Electronics Engineers',
        'file': 'ieee.csl',
        'numeric': True
    },
    'apa': {
        'name': 'APA 7th Edition',
        'description': 'American Psychological Association',
        'file': 'apa.csl',
        'numeric': False
    },
    'chicago': {
        'name': 'Chicago Manual of Style',
        'description': 'Chicago author-date style',
        'file': 'chicago.csl',
        'numeric': False
    }
}


# =============================================================================
# CSL STYLE MANAGEMENT
# =============================================================================

def get_csl_style(style_name: str = 'ieee') -> str:
    """
    Get CSL style file name.
    
    Args:
        style_name: Name of citation style ('ieee', 'apa', 'chicago', etc.)
        
    Returns:
        CSL filename
        
    Raises:
        ValueError: If style not found
    """
    if style_name not in AVAILABLE_CSL_STYLES:
        available = ', '.join(AVAILABLE_CSL_STYLES.keys())
        raise ValueError(
            f"CSL style '{style_name}' not found. "
            f"Available styles: {available}"
        )
    
    return AVAILABLE_CSL_STYLES[style_name]['file']


def get_csl_path(style_name: str = 'ieee') -> Path:
    """
    Get absolute path to CSL file.
    
    Args:
        style_name: Name of citation style
        
    Returns:
        Absolute path to CSL file
        
    Raises:
        FileNotFoundError: If CSL file not found
    """
    # Get package root directory
    package_root = Path(__file__).parent.parent  # ePy_docs/
    
    # CSL files stored in config/assets/csl/
    csl_dir = package_root / 'config' / 'assets' / 'csl'
    
    csl_filename = get_csl_style(style_name)
    csl_path = csl_dir / csl_filename
    
    if not csl_path.exists():
        raise FileNotFoundError(
            f"CSL file not found: {csl_path}\n"
            f"Style: {style_name}"
        )
    
    return csl_path.resolve()


def list_csl_styles() -> List[str]:
    """Return list of available CSL style names."""
    return list(AVAILABLE_CSL_STYLES.keys())


def get_csl_info(style_name: str = 'ieee') -> Dict[str, Any]:
    """
    Get information about CSL style.
    
    Args:
        style_name: Name of citation style
        
    Returns:
        Dictionary with style information
    """
    if style_name not in AVAILABLE_CSL_STYLES:
        raise ValueError(f"CSL style '{style_name}' not found")
    
    return AVAILABLE_CSL_STYLES[style_name].copy()


# =============================================================================
# BIBLIOGRAPHY MANAGEMENT
# =============================================================================

def create_bibliography_file(
    output_path: Path,
    entries: List[Dict[str, str]] = None
) -> Path:
    """
    Create BibTeX bibliography file.
    
    Args:
        output_path: Path to save .bib file
        entries: List of bibliography entries (optional)
        
    Returns:
        Path to created bibliography file
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Default empty bibliography
    if entries is None:
        entries = []
    
    # Generate BibTeX content
    bibtex_content = ""
    for entry in entries:
        bibtex_content += _format_bibtex_entry(entry) + "\n\n"
    
    # Write to file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(bibtex_content)
    
    return output_path


def get_default_bibliography_path() -> Path:
    """
    Get path to default bibliography file.
    
    Returns:
        Path to references.bib in config/assets/bibliography/
    """
    package_root = Path(__file__).parent.parent
    bib_path = package_root / 'config' / 'assets' / 'bibliography' / 'references.bib'
    
    return bib_path.resolve()


def copy_bibliography_to_output(
    source_path: Path,
    output_dir: Path,
    filename: str = 'references.bib'
) -> Path:
    """
    Copy bibliography file to output directory.
    
    Args:
        source_path: Source bibliography file
        output_dir: Destination directory
        filename: Output filename
        
    Returns:
        Path to copied bibliography file
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    dest_path = output_dir / filename
    
    shutil.copy2(source_path, dest_path)
    
    return dest_path


# =============================================================================
# CITATION UTILITIES
# =============================================================================

def format_citation(citation_key: str, style: str = 'pandoc') -> str:
    """
    Format citation for markdown/Quarto.
    
    Args:
        citation_key: BibTeX citation key
        style: Citation style ('pandoc', 'latex')
        
    Returns:
        Formatted citation string
    """
    if style == 'pandoc':
        return f"[@{citation_key}]"
    elif style == 'latex':
        return f"\\cite{{{citation_key}}}"
    else:
        return f"[@{citation_key}]"


def format_multiple_citations(
    citation_keys: List[str],
    style: str = 'pandoc'
) -> str:
    """
    Format multiple citations.
    
    Args:
        citation_keys: List of citation keys
        style: Citation style
        
    Returns:
        Formatted citation string
    """
    if style == 'pandoc':
        keys_str = '; '.join([f"@{key}" for key in citation_keys])
        return f"[{keys_str}]"
    elif style == 'latex':
        keys_str = ','.join(citation_keys)
        return f"\\cite{{{keys_str}}}"
    else:
        keys_str = '; '.join([f"@{key}" for key in citation_keys])
        return f"[{keys_str}]"


# =============================================================================
# BIBTEX HELPERS
# =============================================================================

def _format_bibtex_entry(entry: Dict[str, str]) -> str:
    """
    Format dictionary as BibTeX entry.
    
    Args:
        entry: Dictionary with entry fields (type, key, author, title, etc.)
        
    Returns:
        Formatted BibTeX entry
    """
    entry_type = entry.get('type', 'article')
    entry_key = entry.get('key', 'unknown')
    
    bibtex = f"@{entry_type}{{{entry_key},\n"
    
    # Add fields
    for field, value in entry.items():
        if field not in ['type', 'key']:
            bibtex += f"    {field} = {{{value}}},\n"
    
    bibtex += "}"
    
    return bibtex


def validate_citation_key(citation_key: str) -> bool:
    """
    Validate citation key format.
    
    Args:
        citation_key: Citation key to validate
        
    Returns:
        True if valid
        
    Raises:
        ValueError: If citation key is invalid
    """
    if not citation_key:
        raise ValueError("Citation key cannot be empty")
    
    # BibTeX keys should not contain spaces or special characters
    invalid_chars = [' ', '\t', '\n', '{', '}', ',', '=', '#', '%']
    for char in invalid_chars:
        if char in citation_key:
            raise ValueError(
                f"Citation key '{citation_key}' contains invalid character: '{char}'"
            )
    
    return True


# =============================================================================
# REFERENCE CONFIGURATION
# =============================================================================

def get_reference_config(
    csl_style: str = 'ieee',
    bibliography_path: Optional[Path] = None
) -> Dict[str, Any]:
    """
    Generate reference configuration for Quarto.
    
    Args:
        csl_style: CSL style name
        bibliography_path: Path to bibliography file (optional)
        
    Returns:
        Dictionary with bibliography and CSL configuration
    """
    config = {}
    
    # CSL style
    try:
        csl_path = get_csl_path(csl_style)
        config['csl'] = str(csl_path)
    except FileNotFoundError:
        # Use default if not found
        pass
    
    # Bibliography
    if bibliography_path and bibliography_path.exists():
        config['bibliography'] = str(bibliography_path)
    else:
        # Try default bibliography
        try:
            default_bib = get_default_bibliography_path()
            if default_bib.exists():
                config['bibliography'] = str(default_bib)
        except:
            pass
    
    return config
