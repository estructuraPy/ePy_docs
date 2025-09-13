"""Configuration system for ePy_docs universe.

Constitutional portal providing complete configurations without legacy contamination.
"""

import os
from typing import Dict, Any

def initialize_report_config(layout_style: str, sync_files: bool = False, document_name: str = None) -> Dict[str, Any]:
    """Initialize complete configuration for report writing.
    
    Args:
        layout_style: Layout style from universal set (academic, technical, corporate, minimal, classic, scientific, professional, creative)
        sync_files: Sync control (False=cache, True=synchronize)
        document_name: Document name override
        
    Returns:
        Complete configuration dictionary with all required realms
        
    Raises:
        ValueError: Invalid layout_style or missing configuration
    """
    # Validate dimensional requirements
    UNIVERSAL_LAYOUTS = {'academic', 'technical', 'corporate', 'minimal', 'classic', 'scientific', 'professional', 'creative'}
    if layout_style not in UNIVERSAL_LAYOUTS:
        raise ValueError(f"Invalid layout_style '{layout_style}'. Must be one of: {UNIVERSAL_LAYOUTS}")
    
    # Import from authorized realms via FILES world
    from ePy_docs.files.data import _load_cached_files
    from ePy_docs.components.setup import _resolve_config_path
    from ePy_docs.components.project_info import get_project_config_data
    from ePy_docs.components.colors import get_colors_config
    from ePy_docs.components.pages import set_current_layout
    
    # Initialize appearance dimension
    set_current_layout(layout_style)
    
    # Load configurations through official commercial offices
    setup_config = _load_cached_files(_resolve_config_path('components/setup', sync_files), sync_files)
    project_config = get_project_config_data(sync_files=sync_files)
    colors_config = get_colors_config(sync_files)
    report_config = _load_cached_files(_resolve_config_path('components/report', sync_files), sync_files)
    
    # Validate layout existence in report realm
    report_layouts = report_config.get('layouts', {})
    if layout_style not in report_layouts:
        raise ValueError(f"Layout '{layout_style}' not configured in report realm")
    
    report_layout = report_layouts[layout_style]
    layout_colors = colors_config['layout_styles'][layout_style]
    
    # Initialize units system
    units_config = _initialize_units_system(sync_files)
    
    # Calculate paths with strict validation
    current_dir = os.getcwd()
    directories = setup_config.get('directories')
    if not directories or 'report' not in directories:
        raise ValueError("Invalid setup configuration: missing directories.report")
    
    output_dir = os.path.join(current_dir, directories['report'])
    
    # CONSTITUTIONAL CHANGE: configurator.py NO longer accesses report_name
    # Only report.py (ReportWriter) has constitutional access to report_name
    # Use generic naming for configuration, ReportWriter will handle final naming
    
    # CONSTITUTIONAL: configurator.py has NO ACCESS to report_name
    # ReportWriter will generate constitutional filename directly
    
    # Ensure output directory existence only
    os.makedirs(output_dir, exist_ok=True)
    
    # Sync files if required
    if sync_files:
        from ePy_docs.components.pages import sync_ref
        sync_ref(sync_files=sync_files)
    
    return {
        'layout_style': layout_style,
        'sync_files': sync_files,
        'units_config': units_config,
        'project_config': project_config,
        'setup_config': setup_config,
        'report_config': report_config,
        'report_layout': report_layout,
        'layout_colors': layout_colors,
        'output_dir': output_dir,
        'current_dir': current_dir
    }


def initialize_paper_config(layout_style: str, sync_files: bool = False, document_name: str = None) -> Dict[str, Any]:
    """Initialize complete configuration for paper writing.
    
    Args:
        layout_style: Layout style from universal set (academic, technical, corporate, minimal, classic, scientific, professional, creative)
        sync_files: Sync control (False=cache, True=synchronize)
        document_name: Document name override
        
    Returns:
        Complete configuration dictionary with all required realms
        
    Raises:
        ValueError: Invalid layout_style or missing configuration
    """
    # Validate dimensional requirements
    UNIVERSAL_LAYOUTS = {'academic', 'technical', 'corporate', 'minimal', 'classic', 'scientific', 'professional', 'creative'}
    if layout_style not in UNIVERSAL_LAYOUTS:
        raise ValueError(f"Invalid layout_style '{layout_style}'. Must be one of: {UNIVERSAL_LAYOUTS}")
    
    # Import from authorized realms via FILES world
    from ePy_docs.files.data import _load_cached_files
    from ePy_docs.components.setup import _resolve_config_path
    from ePy_docs.components.project_info import get_project_config_data
    from ePy_docs.components.pages import set_current_layout
    
    # Initialize appearance dimension
    set_current_layout(layout_style)
    
    # Load configurations through official commercial offices
    setup_config = _load_cached_files(_resolve_config_path('components/setup', sync_files), sync_files)
    project_config = get_project_config_data(sync_files=sync_files)
    paper_config = _load_cached_files(_resolve_config_path('components/paper', sync_files), sync_files)
    
    # Validate layout existence in paper realm
    paper_layouts = paper_config.get('layouts', {})
    if layout_style not in paper_layouts:
        raise ValueError(f"Layout '{layout_style}' not configured in paper realm")
    
    paper_layout = paper_layouts[layout_style]
    
    # Initialize units system
    units_config = _initialize_units_system(sync_files)
    
    # Calculate paths with strict validation
    current_dir = os.getcwd()
    directories = setup_config.get('directories')
    if not directories:
        raise ValueError("Invalid setup configuration: missing directories")
    
    paper_dir = directories.get('paper', directories.get('report'))
    if not paper_dir:
        raise ValueError("Invalid setup configuration: missing directories.paper and directories.report")
    
    output_dir = os.path.join(current_dir, paper_dir)
    
    # CONSTITUTIONAL CHANGE: configurator.py NO longer accesses paper_name  
    # Only paper.py (PaperWriter) has constitutional access to paper_name
    # CONSTITUTIONAL: configurator.py has NO ACCESS to paper_name
    # PaperWriter will generate constitutional filename directly
    
    # Ensure output directory existence only
    os.makedirs(output_dir, exist_ok=True)
    
    # Sync files if required
    if sync_files:
        from ePy_docs.components.pages import sync_ref
        sync_ref(sync_files=sync_files)
    
    return {
        'layout_style': layout_style,
        'sync_files': sync_files,
        'units_config': units_config,
        'project_config': project_config,
        'paper_config': paper_config,
        'paper_layout': paper_layout,
        'output_dir': output_dir,
        'current_dir': current_dir
    }


def _initialize_units_system(sync_files: bool) -> Dict[str, Any]:
    """Initialize units system from authorized realm.
    
    Args:
        sync_files: Sync control
        
    Returns:
        Units configuration dictionary
        
    Raises:
        ValueError: Invalid units configuration
    """
    from ePy_docs.units.converter import initialize_converter_databases
    from ePy_docs.files.data import _load_cached_files
    from ePy_docs.components.setup import _resolve_config_path
    
    # Load units configuration through FILES world
    units_path = _resolve_config_path('units/units', sync_files)
    units_config = _load_cached_files(units_path, sync_files)
    
    if not units_config:
        raise ValueError("Units configuration not found")
    
    # Initialize converter with validated paths
    units_dir = os.path.dirname(units_path)
    required_files = {
        'conversion': os.path.join(units_dir, 'conversion.json'),
        'prefix': os.path.join(units_dir, 'prefix.json'),
        'aliases': os.path.join(units_dir, 'aliases.json')
    }
    
    for name, path in required_files.items():
        if not os.path.exists(path):
            raise ValueError(f"Required {name} file not found: {path}")
    
    initialize_converter_databases(
        conversion_file=required_files['conversion'],
        prefix_file=required_files['prefix'],
        aliases_file=required_files['aliases'],
        format_file=None,
        units_file=units_path
    )
    
    return units_config


def get_unit_from_config(units_config: Dict[str, Any], category: str, unit_type: str) -> str:
    """Extract unit from configuration.
    
    Args:
        units_config: Units realm configuration
        category: Unit category
        unit_type: Specific unit type
        
    Returns:
        Unit string
        
    Raises:
        ValueError: Invalid configuration path
    """
    from ePy_docs.units.converter import get_unit_from_config as _get_unit
    return _get_unit(units_config, category, unit_type)


def get_units_config(sync_files: bool = False) -> Dict[str, Any]:
    """Get units configuration from units realm.
    
    Args:
        sync_files: Sync control
        
    Returns:
        Units configuration dictionary
    """
    from ePy_docs.files.data import _load_cached_files
    from ePy_docs.components.setup import _resolve_config_path
    
    return _load_cached_files(_resolve_config_path('units/units', sync_files), sync_files)


def get_project_config(sync_files: bool = False) -> Dict[str, Any]:
    """Get project configuration from project realm.
    
    Args:
        sync_files: Sync control
        
    Returns:
        Project configuration dictionary
    """
    from ePy_docs.components.project_info import get_project_config_data
    return get_project_config_data(sync_files=sync_files)


__all__ = [
    'initialize_report_config',
    'initialize_paper_config',
    'get_unit_from_config',
    'get_units_config',
    'get_project_config'
]