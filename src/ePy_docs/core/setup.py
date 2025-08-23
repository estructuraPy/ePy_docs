"""Setup and configuration utilities for ePy_docs.

Clean configuration loading from setup.json without fallbacks or hardcoded paths.
"""

import os
import json
from typing import Dict, Any


def load_setup_config(sync_json: bool = True) -> Dict[str, Any]:
    """Load configuration from setup.json.
    
    Args:
        sync_json: Whether to sync JSON files (parameter kept for compatibility but ignored)
    
    Returns:
        Configuration dictionary from setup.json
        
    Raises:
        FileNotFoundError: If setup.json is not found
        json.JSONDecodeError: If setup.json is invalid
    """
    setup_path = os.path.join(os.path.dirname(__file__), 'setup.json')
    
    with open(setup_path, 'r', encoding='utf-8') as file:
        return json.load(file)


def get_output_directories() -> Dict[str, str]:
    """Get all directories from setup.json configuration.
    
    Returns:
        Dictionary with all directory paths from setup.json
    """
    setup_config = load_setup_config(sync_json=False)
    return setup_config['directories']


def _load_cached_config(config_type: str) -> Dict[str, Any]:
    """Load configuration from setup.json paths.

    Args:
        config_type: Type of configuration to load (direct filename without .json)

    Returns:
        Dictionary containing configuration data

    Raises:
        FileNotFoundError: If configuration file not found
        json.JSONDecodeError: If configuration file is invalid
    """
    directories = get_output_directories()
    
    # Get the project root directory (where we are running from)
    current_dir = os.getcwd()
    
    # Build path to config file - support nested paths
    if '/' in config_type:
        # Handle nested paths like 'components/colors'
        config_file = os.path.join(current_dir, directories['configuration'], f'{config_type}.json')
    else:
        # Handle direct names like 'colors' (assume in components)
        config_file = os.path.join(current_dir, directories['configuration'], 'components', f'{config_type}.json')
    
    with open(config_file, 'r', encoding='utf-8') as file:
        return json.load(file)


def setup_library_core(layout=None, sync_files=True, base_dir=None):
    """Core library setup function.
    
    Args:
        layout: Layout to use for the report
        sync_files: Whether to sync configuration files
        base_dir: Base directory for the project
        
    Returns:
        Dictionary with setup result including project config, configs, and layout
    """
    if layout is None:
        raise ValueError("Layout parameter is required")
    
    # Load setup configuration (ignore sync_files parameter for now)
    setup_config = load_setup_config()
    
    # Load component configurations
    configs = {}
    try:
        configs['colors'] = _load_cached_config('colors')
        configs['page'] = _load_cached_config('page')
        configs['tables'] = _load_cached_config('tables')
        configs['notes'] = _load_cached_config('notes')
        configs['images'] = _load_cached_config('images')
        configs['equations'] = _load_cached_config('equations')
        configs['units'] = _load_cached_config('units/units')
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Warning: Could not load some configuration files: {e}")
        configs = {}
    
    return {
        'project_config': setup_config,
        'configs': configs,
        'layout': layout,
        'sync_files': sync_files
    }


def setup_project(layout=None, sync_files=True):
    """Setup project with layout and configuration.
    
    Args:
        layout: Layout to use
        sync_files: Whether to sync configuration files
        
    Returns:
        Setup result dictionary
    """
    return setup_library_core(layout=layout, sync_files=sync_files)


class ProjectSettings:
    """Simple settings container for project configuration."""
    def __init__(self, sync_json=True):
        self.sync_json = sync_json


class ProjectConfig:
    """Project configuration container."""
    def __init__(self, settings=None):
        self.settings = settings or ProjectSettings()


def get_current_project_config():
    """Get the current project configuration.
    
    Returns:
        ProjectConfig instance with sync_json setting from setup.json
    """
    try:
        setup_config = load_setup_config()
        # Check if sync_json is defined in setup.json settings
        settings_dict = setup_config.get('settings', {})
        sync_json = settings_dict.get('sync_json', True)  # Default to True
        
        settings = ProjectSettings(sync_json=sync_json)
        return ProjectConfig(settings=settings)
    except (FileNotFoundError, json.JSONDecodeError):
        # If no setup.json or invalid, return default config
        return ProjectConfig()


__all__ = [
    'load_setup_config',
    'get_output_directories', 
    '_load_cached_config',
    'setup_library_core',
    'setup_project',
    'get_current_project_config',
    'ProjectConfig',
    'ProjectSettings'
]
