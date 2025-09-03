"""Clean setup initialization for ePy_docs notebooks.
Direct configuration loading with strict sync_files control.
"""

import os
from ePy_docs.components.pages import set_current_layout

def setup_library(layout_name=None, sync_files: bool = False, notebook_dir=None):
    """Initialize ePy_docs library with direct configuration access."""
    if layout_name is None:
        raise ValueError("layout_name is required")
    
    from ePy_docs.core.setup import _load_cached_files, get_filepath
    from pathlib import Path
    
    # Load setup.json directly
    setup_config_path = Path(__file__).parent.parent / 'core' / 'setup.json'
    setup_config = _load_cached_files(str(setup_config_path), sync_files)
    
    # Load colors configuration (always needed for layout)
    colors_config = _load_cached_files(get_filepath('files.configuration.styling.colors_json'), sync_files)
    layout_info = colors_config['layout_styles'][layout_name]
    
    # Load project config from centralized project_info (no hardcoded as per Lord Supremo)
    from ePy_docs.components.project_info import get_project_config_data
    project_config = get_project_config_data(sync_files=sync_files)
    
    return {
        'layout_name': layout_name,
        'sync_files': sync_files,
        'setup_config': setup_config,
        'base_dir': notebook_dir or os.getcwd(),
        'project_config': project_config,
        'configs': {},
        'layout': layout_info
    }

def quick_setup(layout_name=None, sync_files: bool = False, responsability=False):
    """Clean setup with direct initialization."""
    if layout_name is None:
        raise ValueError("layout_name is required")
    
    result = setup_library(layout_name=layout_name, sync_files=sync_files)
    set_current_layout(layout_name)
    
    setup_config = _setup_directories(sync_files=sync_files)
    _initialize_subsystems(result, responsability, sync_files)
    _configure_globals(result, setup_config, sync_files, responsability)  # Mover después de _initialize_subsystems
    
    # Agregar configuraciones adicionales al resultado
    from ePy_docs.core.setup import _load_cached_files, get_filepath
    from ePy_docs.components.project_info import get_project_config_data
    
    # Cargar configuración completa del proyecto
    result['project_config'] = get_project_config_data(sync_files=sync_files)
    
    # Hacer el converter disponible globalmente para compatibilidad con código anterior
    import builtins
    if hasattr(builtins, 'converter'):
        globals()['converter'] = builtins.converter
        # También inyectar en el frame del caller para máxima compatibilidad
        import sys
        if len(sys._getframe(1).f_locals) > 0:
            sys._getframe(1).f_globals['converter'] = builtins.converter
    
    return result

def _setup_directories(sync_files: bool):
    """Create directories from setup configuration."""
    from ePy_docs.core.setup import _load_cached_files, get_filepath
    from pathlib import Path

    # Load setup.json directly
    setup_config_path = Path(__file__).parent.parent / 'core' / 'setup.json'
    setup_config = _load_cached_files(str(setup_config_path), sync_files)
    current_dir = os.getcwd()

    for dir_key, dir_path in setup_config['directories'].items():
        # Skip creation of configuration directory when sync_files=False
        if not sync_files and (dir_path == 'data/configuration' or 'configuration' in dir_path):
            continue
        os.makedirs(os.path.join(current_dir, dir_path), exist_ok=True)

    # Sync reference files (.bib and .csl) when sync_files=True
    if sync_files:
        from ePy_docs.components.pages import sync_ref
        sync_ref(sync_files=sync_files)

    return setup_config

def _configure_globals(result, setup_config, sync_files, responsability):
    """Configure global variables."""
    import builtins
    builtins.project_config = result['project_config']
    builtins.configs = result['configs']
    builtins.current_layout = result['layout']
    builtins.sync_files_enabled = sync_files
    builtins.responsability_enabled = responsability
    builtins.setup_config = setup_config
    
    # Variables que el usuario puede usar directamente
    builtins.writer = result.get('writer')
    builtins.units_config = result.get('units_config')
    builtins.converter = result.get('converter')  # Agregar converter a builtins
    
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
    """Initialize subsystems."""
    units_config, converter = _setup_units_system(sync_files=sync_files)
    result['units_config'] = units_config
    result['converter'] = converter
    
    writer = _setup_writer_system(result['project_config'], responsability, sync_files)
    if writer:
        result['writer'] = writer
    
    _setup_file_system()
def _setup_directory_structure(sync_files: bool):
    """Create and configure directory structure."""
    setup_config = _setup_directories(sync_files)
    
    # Load core configurations
    from ePy_docs.components.project_info import load_project_info
    from ePy_docs.core.base import load_all_configs
    from ePy_docs.components.pages import get_current_layout
    
    result = {
        'layout': get_current_layout(),
        'project_config': load_project_info(sync_files=sync_files),
        'configs': load_all_configs(sync_files=sync_files)
    }
    
    _configure_globals(result, setup_config, sync_files, True)  # responsability default to True
    return result

def _setup_units_system(sync_files: bool):
    """Initialize units system."""
    import builtins
    from ePy_docs.units.converter import UnitConverter, get_unit_from_config
    from ePy_docs.core.setup import _load_cached_files, get_filepath
    
    units_config = _load_cached_files(get_filepath('files.configuration.units.units_json'), sync_files)
    
    if not hasattr(builtins, 'configs'):
        builtins.configs = {}
    builtins.configs['units'] = units_config
    
    length_unit = get_unit_from_config(units_config, 'structure_dimensions', 'length')
    area_unit = get_unit_from_config(units_config, 'structure_dimensions', 'structure_area')
    volume_unit = get_unit_from_config(units_config, 'section_dimensions', 'length3')
    force_unit = get_unit_from_config(units_config, 'forces', 'force')
    
    builtins.length_unit = length_unit
    builtins.area_unit = area_unit  
    builtins.volume_unit = volume_unit
    builtins.force_unit = force_unit
    
    # Crear el converter y ponerlo en builtins
    converter = UnitConverter.create_default(sync_files=sync_files)
    builtins.converter = converter
    
    return units_config, converter

def _setup_writer_system(project_config, responsability=False, sync_files: bool = False):
    """Initialize report writer system."""
    import builtins
    from ePy_docs.api.report import ReportWriter
    from ePy_docs.core.setup import _load_cached_files, get_filepath
    from ePy_docs.components.project_info import get_project_config_data
    from pathlib import Path
    
    current_dir = os.getcwd()
    
    # Load setup.json directly
    setup_config_path = Path(__file__).parent.parent / 'core' / 'setup.json'
    setup_config = _load_cached_files(str(setup_config_path), sync_files)
    report_dir_name = setup_config['directories']['report']
    local_report_dir = os.path.join(current_dir, report_dir_name)
    
    project_config_data = get_project_config_data(sync_files=sync_files)
    report_name = project_config_data['project']['report']
    
    output_config = setup_config.get('output', {})
    report_filename = output_config.get('report_filename', f'{report_name}.pdf')
    report_path = os.path.join(local_report_dir, report_filename)
    auto_print = output_config.get('auto_print', True)
    
    writer = ReportWriter(file_path=report_path, output_dir=local_report_dir, auto_print=auto_print, sync_files=sync_files)
    
    if hasattr(builtins, 'crossref_config'):
        crossref_config = builtins.crossref_config
        if hasattr(writer, 'configure_crossref'):
            writer.configure_crossref(crossref_config)
        else:
            writer._crossref_config = crossref_config
    
    if responsability:
        add_professional_responsibility_page(writer, sync_files=sync_files)
    
    builtins.writer = writer
    return writer

def _setup_file_system():
    """Initialize file manager system."""
    import builtins
    from ePy_docs.api.file_management import FileManager
    
    csv_defaults = {}
    if hasattr(builtins, 'configs') and 'csv_defaults' in builtins.configs:
        csv_defaults = builtins.configs['csv_defaults']
    
    file_manager = FileManager(base_dir=os.getcwd())
    
    if csv_defaults and hasattr(file_manager, 'configure_csv_defaults'):
        file_manager.configure_csv_defaults(csv_defaults)
    elif csv_defaults:
        file_manager._csv_defaults = csv_defaults
            
    builtins.csv_defaults = csv_defaults
    builtins.files = file_manager

def add_professional_responsibility_page(writer, sync_files: bool):
    """Add professional responsibility page to any writer instance."""
    from ePy_docs.components.project_info import add_responsibility_text
    add_responsibility_text(writer, sync_files=sync_files)
    return True

