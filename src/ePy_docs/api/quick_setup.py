"""
Simple setup initialization for ePy_docs notebooks.
Provides direct access to core functionality without complex logic.

This module integrates with setup.json to provide:
- Automatic directory structure creation based on setup.json directories section
- CSV defaults configuration from setup.json csv_defaults section  
- Quarto and crossref configuration from setup.json formats_quarto section
- Report configuration labels from setup.json report_config section
- Comprehensive file path management based on setup.json files section
- Professional responsibility pages using the complete project_info system

The quick_setup function eliminates redundancy by centralizing all configuration
in setup.json and making it available throughout the system.

Key improvements:
- Uses professional responsibility system with project info, consultants, and copyright
- Integrates with existing TextFormatter and setup configuration
- Provides fallback for basic responsibility page if professional system unavailable
- All responsibility content sourced from JSON configuration files
"""

import os
import json


def setup_library(layout=None, sync_files=True, notebook_dir=None):
    """
    Initialize ePy_docs library with minimal configuration required.
    
    Args:
        layout: Layout to use (REQUIRED)
        sync_files: Whether to sync configuration files from templates
        notebook_dir: Directory where notebook is located (auto-detected if None)
        
    Returns:
        Dict with initialized core components
        
    Raises:
        ValueError: If layout is not specified
        RuntimeError: If configuration fails
    """
    if layout is None:
        raise ValueError("Layout parameter is required. Available: 'corporate', 'academic', 'technical', 'minimal', 'classic', 'scientific', 'professional', 'creative'")
    
    # Delegate all logic to core.setup
    from ePy_docs.core.setup import setup_library_core
    
    return setup_library_core(
        layout=layout,
        sync_files=sync_files,
        base_dir=notebook_dir
    )


def quick_setup(layout=None, sync_files=True, responsability=False):
    """
    Quick setup with automatic initialization of all convenience systems.
    Initializes core library + units system + report writer automatically.
    Uses setup.json configuration for comprehensive directory and file management.
    
    Args:
        layout: Layout to use for the report
        sync_files: Whether to sync configuration files
        responsability: Whether to add professional responsibility page to writer
    """
    if layout is None:
        raise ValueError("Layout is required. Available: 'corporate', 'academic', 'technical', 'minimal', 'classic', 'scientific', 'professional', 'creative'")
    
    # Initialize core library
    result = setup_library(layout=layout, sync_files=sync_files)
    
    # Setup comprehensive directory structure and get setup config
    setup_config = _setup_directory_structure(sync_files=sync_files)
    
    # Make setup configuration available globally
    import builtins
    builtins.project_config = result['project_config']
    builtins.configs = result['configs']
    builtins.current_layout = result['layout']
    builtins.sync_files_enabled = sync_files
    builtins.responsability_enabled = responsability
    builtins.setup_config = setup_config  # Add setup.json config to global scope
    
    # Integrate setup.json configurations into the configs
    if setup_config:
        # Add CSV defaults for data processing
        if 'csv_defaults' in setup_config:
            builtins.configs['csv_defaults'] = setup_config['csv_defaults']
        
        # Add report configuration labels and formats
        if 'report_config' in setup_config:
            if 'report' not in builtins.configs:
                builtins.configs['report'] = {}
            builtins.configs['report'].update(setup_config['report_config'])
        
        # Add Quarto configuration and crossref settings
        if 'formats_quarto' in setup_config:
            if 'quarto' not in builtins.configs:
                builtins.configs['quarto'] = {}
            builtins.configs['quarto'].update(setup_config['formats_quarto'])
            
            # Set crossref configuration globally to avoid redundancy
            if 'crossref' in setup_config['formats_quarto']:
                builtins.crossref_config = setup_config['formats_quarto']['crossref']
    
    sync_status = "✅ Enabled" if sync_files else "❌ Disabled"
    resp_status = "✅ Enabled" if responsability else "❌ Disabled"
    print(f"🎯 ePy_docs library initialized:")
    print(f"   📋 Layout: {layout}")
    print(f"   🔄 Config sync: {sync_status}")
    print(f"   ⚖️ Responsibility page: {resp_status}")
    if setup_config:
        print(f"   📋 Project setup: ✅ Loaded from setup.json")
        if 'csv_defaults' in setup_config:
            print(f"   📊 CSV defaults: ✅ Configured")
        if 'formats_quarto' in setup_config:
            print(f"   📝 Quarto formats: ✅ Configured")
    
    # Auto-initialize subsystems
    units_result = _setup_units_system()
    if units_result:
        result.update(units_result)
        print("🔢 Units system ready - Global functions available: convert(), convert_to_default_length(), convert_to_default_force()")
    
    writer_result = _setup_writer_system(result['project_config'], responsability=responsability)
    if writer_result:
        result.update(writer_result)
        print("📝 Report writer ready - Global variable available: writer")
    
    files_result = _setup_file_system()
    if files_result:
        result.update(files_result)
        print("📁 File manager ready - Global variable available: files")
    
    print("✅ All systems ready!")
    
    # Add setup_config to result for return
    if setup_config:
        result['setup_config'] = setup_config
    
    return result


def _setup_directory_structure(sync_files=True):
    """Create all directories and subdirectories defined in setup.json configuration.
    
    Args:
        sync_files: Whether to sync configuration files (determines if configuration directory is created)
    """
    try:
        # Get current directory
        current_dir = os.getcwd()
        
        # Import the setup config loader from core.setup
        from ePy_docs.core.setup import load_setup_config
        
        # Use the core setup system to load the configuration
        setup_config = load_setup_config(sync_json=True)
        
        if not setup_config:
            print("⚠️  setup.json not found, using default directory structure")
            # Create basic directories as fallback (configuration only if sync_files is True)
            default_dirs = ["results", "data"]
            if sync_files:
                default_dirs.append("data/configuration")  # Updated to new location
            for dir_name in default_dirs:
                os.makedirs(os.path.join(current_dir, dir_name), exist_ok=True)
            return setup_config
        
        created_dirs = []
        
        # Create directories from setup.json configuration
        if 'directories' in setup_config:
            directories = setup_config['directories']
            
            for dir_key, dir_path in directories.items():
                # Skip configuration directory if sync_files is False
                if dir_key == 'config' and not sync_files:
                    continue
                    
                full_path = os.path.join(current_dir, dir_path)
                os.makedirs(full_path, exist_ok=True)
                created_dirs.append(dir_path)
        
        # Create subdirectories for data files based on input_data configuration
        if 'files' in setup_config and 'input_data' in setup_config['files']:
            data_dir = os.path.join(current_dir, setup_config['directories'].get('data', 'data'))
            input_data_config = setup_config['files']['input_data']
            
            for category_name, category_files in input_data_config.items():
                for file_key, file_path in category_files.items():
                    # Create parent directories for each file path
                    full_file_path = os.path.join(data_dir, file_path)
                    parent_dir = os.path.dirname(full_file_path)
                    if parent_dir and parent_dir != data_dir:
                        os.makedirs(parent_dir, exist_ok=True)
                        relative_parent = os.path.relpath(parent_dir, current_dir)
                        if relative_parent not in created_dirs:
                            created_dirs.append(relative_parent)
        
        # Create subdirectories for configuration files only if sync_files is True
        if sync_files and 'files' in setup_config and 'configuration' in setup_config['files']:
            config_dir = os.path.join(current_dir, setup_config['directories'].get('config', 'configuration'))
            config_files = setup_config['files']['configuration']
            
            for section_name, section_files in config_files.items():
                for file_key, file_path in section_files.items():
                    # Create parent directories for each configuration file
                    full_file_path = os.path.join(config_dir, file_path)
                    parent_dir = os.path.dirname(full_file_path)
                    if parent_dir and parent_dir != config_dir:
                        os.makedirs(parent_dir, exist_ok=True)
                        relative_parent = os.path.relpath(parent_dir, current_dir)
                        if relative_parent not in created_dirs:
                            created_dirs.append(relative_parent)
        
        # Create essential working subdirectories within results directory
        results_dir = os.path.join(current_dir, setup_config['directories'].get('results', 'results'))
        # Only create essential subdirectories that are commonly needed
        essential_subdirs = ['tables', 'figures']  
        for subdir in essential_subdirs:
            sub_path = os.path.join(results_dir, subdir)
            os.makedirs(sub_path, exist_ok=True)
            relative_sub = os.path.relpath(sub_path, current_dir)
            if relative_sub not in created_dirs:
                created_dirs.append(relative_sub)
        
        if created_dirs:
            print(f"📁 Directory structure created: {', '.join(sorted(set(created_dirs)))}")
        
        return setup_config
            
    except Exception as e:
        print(f"⚠️  Error setting up directory structure: {e}")
        # Create basic fallback directories
        current_dir = os.getcwd()
        default_dirs = ["results", "data"]
        if sync_files:
            default_dirs.append("data/configuration")  # Updated to new location
        for dir_name in default_dirs:
            os.makedirs(os.path.join(current_dir, dir_name), exist_ok=True)
        return None


def _setup_units_system():
    """Setup units system with global functions."""
    try:
        import builtins
        from ePy_docs.units.converter import UnitConverter, get_unit_from_config
        
        units_config = builtins.configs['units']
        
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
            _load_cached_config('units/conversion', sync_files=True)
            _load_cached_config('units/aliases', sync_files=True) 
            _load_cached_config('units/format', sync_files=True)
            _load_cached_config('units/prefix', sync_files=True)
        except Exception as sync_error:
            # If sync fails, continue anyway as converter might work with source files
            pass
        
        # Create unit converter
        converter = UnitConverter.create_default()
        
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


def _setup_writer_system(project_config, responsability=False):
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
        
        # Try to get results directory from global config, with fallback to "results"
        try:
            from ePy_docs.core.setup import load_setup_config
            setup_config = load_setup_config(sync_json=False)  # Don't sync, just load
            results_dir_name = setup_config['directories'].get('results', 'results') if setup_config else 'results'
        except:
            results_dir_name = 'results'  # Safe fallback
            
        local_results_dir = os.path.join(current_dir, results_dir_name)
        
        report_filename = output_config.get('report_filename', 'report.pdf')
        report_path = os.path.join(local_results_dir, report_filename)
        auto_print = output_config.get('auto_print', True)
        
        writer = ReportWriter(file_path=report_path, output_dir=local_results_dir, auto_print=auto_print)
        
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
            add_professional_responsibility_page(writer)
        
        builtins.writer = writer
        
        return {'writer': writer}
    except Exception as e:
        print(f"⚠️  Writer system initialization failed: {e}")
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
        print(f"⚠️  File system initialization failed: {e}")
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


def add_professional_responsibility_page(writer):
    """Add professional responsibility page to any writer instance.
    
    This is a convenience function that can be used independently of quick_setup
    to add comprehensive responsibility pages to any report.
    
    Args:
        writer: ReportWriter instance
    
    Returns:
        bool: True if professional system was used, False if fallback was used
    """
    from ePy_docs.components.project_info import add_responsibility_text
    add_responsibility_text(writer)
    return True
    
        

