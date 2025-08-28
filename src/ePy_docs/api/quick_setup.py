"""
Simple setup initialization for ePy_docs notebooks.
Centralizes all configuration in setup.json with automatic directory management.
"""

import os
from ePy_docs.core.layouts import set_current_layout


def setup_library(layout_name=None, sync_files: bool = False, notebook_dir=None):
    """Initialize ePy_docs library with minimal configuration required."""
    if layout_name is None:
        raise ValueError("layout_name parameter is required. Available: 'corporate', 'academic', 'technical', 'minimal', 'classic', 'scientific', 'professional', 'creative'")
    
    from ePy_docs.core.setup import setup_library_core
    return setup_library_core(layout_name=layout_name, sync_files=sync_files, base_dir=notebook_dir)


def quick_setup(layout_name=None, sync_files: bool = False, responsability=False):
    """Quick setup with automatic initialization of all systems."""
    if layout_name is None:
        raise ValueError("layout_name is required. Available: 'corporate', 'academic', 'technical', 'minimal', 'classic', 'scientific', 'professional', 'creative'")
    
    # Initialize core library and set layout
    result = setup_library(layout_name=layout_name, sync_files=sync_files)
    set_current_layout(layout_name)
    
    # Setup directories and get config
    setup_config = _setup_directories(sync_files=sync_files)
    
    # Configure global scope
    _configure_globals(result, setup_config, sync_files, responsability)
    
    # Initialize subsystems
    _initialize_subsystems(result, responsability, sync_files)
    
    return result


def _setup_directories(sync_files: bool):
    """Create directories defined in setup.json."""
    from ePy_docs.core.setup import load_setup_config
    setup_config = load_setup_config(sync_files=sync_files)
    current_dir = os.getcwd()
    
    if 'directories' in setup_config:
        for dir_key, dir_path in setup_config['directories'].items():
            # Skip configuration directory if sync_files is False
            if dir_key == 'configuration' and not sync_files:
                continue
            os.makedirs(os.path.join(current_dir, dir_path), exist_ok=True)
    
    return setup_config


def _configure_globals(result, setup_config, sync_files, responsability):
    """Configure global variables in builtins."""
    import builtins
    builtins.project_config = result['project_config']
    builtins.configs = result['configs']
    builtins.current_layout = result['layout']
    builtins.sync_files_enabled = sync_files
    builtins.responsability_enabled = responsability
    builtins.setup_config = setup_config
    
    if setup_config:
        # Integrate setup.json configurations
        for key in ['csv_defaults', 'report_config', 'formats_quarto']:
            if key in setup_config:
                if key == 'csv_defaults':
                    builtins.configs['csv_defaults'] = setup_config[key]
                elif key == 'report_config':
                    builtins.configs.setdefault('report', {}).update(setup_config[key])
                elif key == 'formats_quarto':
                    builtins.configs.setdefault('quarto', {}).update(setup_config[key])
                    if 'crossref' in setup_config[key]:
                        builtins.crossref_config = setup_config[key]['crossref']


def _initialize_subsystems(result, responsability, sync_files):
    """Initialize all subsystems (units, writer, files)."""
    subsystems = [
        _setup_units_system,
        lambda: _setup_writer_system(result['project_config'], responsability, sync_files),
        _setup_file_system
    ]
    
    for setup_func in subsystems:
        try:
            subsystem_result = setup_func(sync_files=sync_files) if 'sync_files' in setup_func.__code__.co_varnames else setup_func()
            if subsystem_result:
                result.update(subsystem_result)
        except Exception:
            continue  # Skip failed subsystems
def _setup_directory_structure(sync_files: bool):
    """Create and configure directory structure."""
    setup_config = _setup_directories(sync_files)
    
    # Load core configurations
    from ePy_docs.components.project_info import load_project_info
    from ePy_docs.core.base import load_all_configs
    from ePy_docs.core.layouts import get_current_layout
    
    result = {
        'layout': get_current_layout(),
        'project_config': load_project_info(sync_files=sync_files),
        'configs': load_all_configs(sync_files=sync_files)
    }
    
    _configure_globals(result, setup_config, sync_files, True)  # responsability default to True
    return result


def _setup_units_system(sync_files: bool):
    """Setup units system with global functions."""
    try:
        import builtins
        from ePy_docs.units.converter import UnitConverter, get_unit_from_config
        from ePy_docs.core.setup import _load_cached_config
        
        # Load units configuration from setup.json structure
        units_config = _load_cached_config('units/units', sync_files=sync_files)
        
        # Store in builtins for global access
        if not hasattr(builtins, 'configs'):
            builtins.configs = {}
        builtins.configs['units'] = units_config
        
        # Get default units from configuration
        length_unit = get_unit_from_config(units_config, 'structure_dimensions', 'length')
        area_unit = get_unit_from_config(units_config, 'structure_dimensions', 'structure_area')
        volume_unit = get_unit_from_config(units_config, 'section_dimensions', 'length3')
        force_unit = get_unit_from_config(units_config, 'forces', 'force')
        moment_unit = get_unit_from_config(units_config, 'forces', 'moment')
        
        if not all([length_unit, area_unit, volume_unit, force_unit, moment_unit]):
            return None
        
        # Pre-sync all units configuration files to ensure converter can find them
        try:
            from ePy_docs.core.setup import _load_cached_config
            _load_cached_config('units/conversion', sync_files=sync_files)
            _load_cached_config('units/aliases', sync_files=sync_files) 
            _load_cached_config('units/format', sync_files=sync_files)
            _load_cached_config('units/prefix', sync_files=sync_files)
        except Exception as sync_error:
            # If sync fails, continue anyway as converter might work with source files
            pass
        
        # Create unit converter
        converter = UnitConverter.create_default(sync_files=sync_files)
        
        # Make units available globally
        builtins.length_unit = length_unit
        builtins.area_unit = area_unit
        builtins.volume_unit = volume_unit
        builtins.force_unit = force_unit
        builtins.moment_unit = moment_unit
        builtins.converter = converter
        
        # Create conversion functions
        def convert(value, from_unit, to_unit):
            return converter.universal_unit_converter(value, from_unit, to_unit)
        
        def convert_to_default_length(value, from_unit):
            return converter.universal_unit_converter(value, from_unit, length_unit)
        
        def convert_to_default_force(value, from_unit):
            return converter.universal_unit_converter(value, from_unit, force_unit)
        
        # Make functions globally available
        builtins.convert = convert
        builtins.convert_to_default_length = convert_to_default_length
        builtins.convert_to_default_force = convert_to_default_force
        
        return {
            'units': {
                'length_unit': length_unit,
                'area_unit': area_unit, 
                'volume_unit': volume_unit,
                'force_unit': force_unit,
                'moment_unit': moment_unit,
                'converter': converter
            }
        }
    except Exception as e:
        # Debug: print the exception instead of silently returning None
        print(f"⚠️  Units system initialization failed: {e}")
        import traceback
        traceback.print_exc()
        # Provide default values for when configuration is missing
        return {
            'units': {
                'length_unit': 'mm',
                'area_unit': 'mm²', 
                'volume_unit': 'mm³',
                'force_unit': 'kN',
                'moment_unit': 'kN⋅m',
                'converter': None
            }
        }


def _setup_writer_system(project_config, responsability=False, sync_files: bool = False):
    """Setup report writer system with integrated crossref configuration."""
    try:
        import builtins
        from ePy_docs.api.report import ReportWriter
        
        configs = builtins.configs
        
        # Provide defaults if project_info or output section is missing
        output_config = {}
        if 'project_info' in configs and 'output' in configs['project_info']:
            output_config = configs['project_info']['output']
        
        # Use the results directory already created by setup_directory_structure
        current_dir = os.getcwd()
        
        # Try to get report directory from global config
        from ePy_docs.core.setup import load_setup_config
        setup_config = load_setup_config(sync_files=sync_files)  # Use the actual sync_files parameter
        report_dir_name = setup_config['directories']['report']
            
        local_report_dir = os.path.join(current_dir, report_dir_name)
        
        # Get the correct report name from project configuration
        from ePy_docs.components.project_info import get_project_config_data
        project_config_data = get_project_config_data(sync_files=sync_files)  # Use the actual sync_files parameter
        report_name = project_config_data['project']['report']
        
        # Construct the report filename with proper extension
        report_filename = output_config.get('report_filename', f'{report_name}.pdf')
        report_path = os.path.join(local_report_dir, report_filename)
        auto_print = output_config.get('auto_print', True)
        
        writer = ReportWriter(file_path=report_path, output_dir=local_report_dir, auto_print=auto_print, sync_files=sync_files)
        
        # Configure crossref settings from setup.json if available
        if hasattr(builtins, 'crossref_config'):
            crossref_config = builtins.crossref_config
            # Apply crossref configuration to writer if ReportWriter supports it
            if hasattr(writer, 'configure_crossref'):
                writer.configure_crossref(crossref_config)
            else:
                # Store crossref config for use by other components
                writer._crossref_config = crossref_config
        
        # Add professional responsibility page if requested
        if responsability:
            add_professional_responsibility_page(writer, sync_files=sync_files)
        
        builtins.writer = writer
        
        return {'writer': writer}
    except Exception as e:
        print(f"⚠️  Writer system initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def _setup_file_system():
    """Setup file manager system with CSV defaults from setup.json."""
    try:
        import builtins
        from ePy_docs.api.file_management import FileManager
        
        # Get CSV defaults from setup configuration
        csv_defaults = {}
        if hasattr(builtins, 'configs') and 'csv_defaults' in builtins.configs:
            csv_defaults = builtins.configs['csv_defaults']
        
        # Create file manager with CSV defaults
        file_manager = FileManager(base_dir=os.getcwd())
        
        # Configure CSV defaults if FileManager supports it
        if csv_defaults and hasattr(file_manager, 'configure_csv_defaults'):
            file_manager.configure_csv_defaults(csv_defaults)
        elif csv_defaults:
            # Store CSV defaults for manual use
            file_manager._csv_defaults = csv_defaults
            
        # Make CSV defaults available globally for pandas operations
        builtins.csv_defaults = csv_defaults
        
        builtins.files = file_manager
        
        return {'file_manager': file_manager, 'csv_defaults': csv_defaults}
    except Exception as e:
        return None


def get_csv_defaults():
    """Get CSV reading defaults from setup.json configuration."""
    import builtins
    if hasattr(builtins, 'csv_defaults'):
        return builtins.csv_defaults
    return {
        'encoding': 'utf-8-sig',
        'sep': ';',
        'decimal': ',',
        'thousands': None,
        'na_values': ['', 'nan', 'NaN', 'NULL', 'null'],
        'keep_default_na': True,
        'skipinitialspace': True
    }


def get_crossref_config():
    """Get crossref configuration from setup.json."""
    import builtins
    if hasattr(builtins, 'crossref_config'):
        return builtins.crossref_config
    return {
        'chapters': False,
        'execute_echo': False,
        'eq_prefix': 'Ecuación',
        'eq_labels': 'arabic', 
        'fig_prefix': 'Figura',
        'fig_labels': 'arabic',
        'tbl_prefix': 'Tabla',
        'tbl_labels': 'arabic'
    }


def add_professional_responsibility_page(writer, sync_files: bool):
    """Add professional responsibility page to any writer instance.
    
    This is a convenience function that can be used independently of quick_setup
    to add comprehensive responsibility pages to any report.
    
    Args:
        writer: ReportWriter instance
        sync_files: Whether to sync configuration files
    
    Returns:
        bool: True if professional system was used, False if fallback was used
    """
    from ePy_docs.components.project_info import add_responsibility_text
    add_responsibility_text(writer, sync_files=sync_files)
    return True
    
        

