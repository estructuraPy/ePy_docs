"""Setup and configuration utilities for ePy_docs.

Clean configuration loading from setup.json without fallbacks or hardcoded paths.
"""

import os
import json
import re
from typing import Dict, Any, Tuple

# Global temporary cache for configuration overrides
_temp_config_cache = {}
_temp_cache_enabled = True


def set_temp_config_override(config_type: str, key: str, value: Any) -> None:
    """Set a temporary configuration override in memory.
    
    Args:
        config_type: Type of configuration ('report', 'page', etc.)
        key: Configuration key to override
        value: New value for the key
    """
    global _temp_config_cache
    if config_type not in _temp_config_cache:
        _temp_config_cache[config_type] = {}
    _temp_config_cache[config_type][key] = value


def clear_temp_config_cache(config_type: str = None) -> None:
    """Clear temporary configuration cache.
    
    Args:
        config_type: Specific config type to clear, or None to clear all
    """
    global _temp_config_cache
    if config_type is None:
        _temp_config_cache = {}
    elif config_type in _temp_config_cache:
        del _temp_config_cache[config_type]


def disable_temp_cache() -> None:
    """Disable temporary cache (for testing)."""
    global _temp_cache_enabled
    _temp_cache_enabled = False


def enable_temp_cache() -> None:
    """Enable temporary cache."""
    global _temp_cache_enabled
    _temp_cache_enabled = True


def load_setup_config(sync_json: bool = True) -> Dict[str, Any]:
    """Load configuration from setup.json.
    
    Args:
        sync_json: Whether to sync JSON files from source to configuration directory
    
    Returns:
        Configuration dictionary from setup.json
        
    Raises:
        FileNotFoundError: If setup.json is not found
        json.JSONDecodeError: If setup.json is invalid
    """
    import shutil
    
    # Source file path
    src_setup_path = os.path.join(os.path.dirname(__file__), 'setup.json')
    
    if sync_json:
        # Try to get configuration directory from existing setup.json first
        current_dir = os.getcwd()
        config_setup_path = os.path.join(current_dir, 'data', 'configuration', 'core', 'setup.json')
        
        # Sync file if source exists
        if os.path.exists(src_setup_path):
            # Ensure destination directory exists
            os.makedirs(os.path.dirname(config_setup_path), exist_ok=True)
            
            # Copy if destination doesn't exist or source is newer
            if not os.path.exists(config_setup_path) or os.path.getmtime(src_setup_path) > os.path.getmtime(config_setup_path):
                shutil.copy2(src_setup_path, config_setup_path)
        
        # Try to load from config directory first
        if os.path.exists(config_setup_path):
            with open(config_setup_path, 'r', encoding='utf-8') as file:
                return json.load(file)
    
    # Fallback to source file
    if os.path.exists(src_setup_path):
        with open(src_setup_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    
    raise FileNotFoundError(f"setup.json not found in source: {src_setup_path}")


def get_output_directories(sync_json: bool = False) -> Dict[str, str]:
    """Get all directories from setup.json configuration.
    
    Args:
        sync_json: Whether to sync setup.json before reading
    
    Returns:
        Dictionary with all directory paths from setup.json
    """
    setup_config = load_setup_config(sync_json=sync_json)
    return setup_config['directories']


def get_absolute_output_directories(sync_json: bool = False, base_dir: str = None) -> Dict[str, str]:
    """Get all directories from setup.json configuration as absolute paths.
    
    Args:
        sync_json: Whether to sync setup.json before reading
        base_dir: Base directory to resolve relative paths (defaults to current working directory)
    
    Returns:
        Dictionary with all directory paths as absolute paths
    """
    setup_config = load_setup_config(sync_json=sync_json)
    directories = setup_config['directories']
    
    if base_dir is None:
        base_dir = os.getcwd()
    
    absolute_directories = {}
    for key, path in directories.items():
        if os.path.isabs(path):
            absolute_directories[key] = path
        else:
            absolute_directories[key] = os.path.join(base_dir, path)
    
    return absolute_directories


def _load_cached_config(config_type: str, sync_files: bool = None) -> Dict[str, Any]:
    """Load configuration from setup.json paths with optional synchronization.

    Args:
        config_type: Type of configuration to load (direct filename without .json)
        sync_files: Whether to sync files from src to configuration directory

    Returns:
        Dictionary containing configuration data

    Raises:
        FileNotFoundError: If configuration file not found
        json.JSONDecodeError: If configuration file is invalid
    """
    import shutil
    import os
    
    # Default sync_files to True if not provided (avoiding recursion)
    if sync_files is None:
        sync_files = True
    
    # Load setup config directly without recursive calls
    setup_config = load_setup_config(sync_json=False)  # Don't sync to avoid recursion
    directories = setup_config['directories']
    
    # Get the project root directory (where we are running from)
    current_dir = os.getcwd()
    
    # Build path to config file - support nested paths
    if '/' in config_type:
        # Handle nested paths like 'units/units'
        config_file = os.path.join(current_dir, directories['configuration'], f'{config_type}.json')
        # For source file, map to src structure
        if config_type.startswith('units/'):
            src_file = os.path.join(os.path.dirname(__file__), '..', config_type.replace('/', os.sep) + '.json')
        else:
            src_file = os.path.join(os.path.dirname(__file__), '..', 'components', os.path.basename(config_type) + '.json')
    else:
        # Handle direct names like 'colors', 'report' (assume in components)
        config_file = os.path.join(current_dir, directories['configuration'], 'components', f'{config_type}.json')
        src_file = os.path.join(os.path.dirname(__file__), '..', 'components', f'{config_type}.json')
    
    # Sync files if requested and source exists
    if sync_files and os.path.exists(src_file):
        # Ensure destination directory exists
        os.makedirs(os.path.dirname(config_file), exist_ok=True)
        
        # Copy if destination doesn't exist or source is newer
        if not os.path.exists(config_file) or os.path.getmtime(src_file) > os.path.getmtime(config_file):
            shutil.copy2(src_file, config_file)
    
    # Try to load from config directory first
    if os.path.exists(config_file):
        with open(config_file, 'r', encoding='utf-8') as file:
            config_data = json.load(file)
    else:
        # Configuration file must exist
        raise FileNotFoundError(f"Configuration file not found: {config_file}")
    
    # Apply temporary overrides if cache is enabled
    global _temp_config_cache, _temp_cache_enabled
    if _temp_cache_enabled and config_type in _temp_config_cache:
        overrides = _temp_config_cache[config_type]
        for key, value in overrides.items():
            config_data[key] = value
    
    return config_data


def setup_library_core(layout_name=None, sync_files=True, base_dir=None):
    """Core library setup function.
    
    Args:
        layout_name: Layout to use for the report
        sync_files: Whether to sync configuration files
        base_dir: Base directory for the project
        
    Returns:
        Dictionary with setup result including project config, configs, and layout
    """
    if layout_name is None:
        raise ValueError("Layout parameter is required")
    
    # Load setup configuration with sync_files parameter
    setup_config = load_setup_config(sync_json=sync_files)
    
    # Load component configurations with sync_files parameter
    configs = {}
    try:
        configs['colors'] = _load_cached_config('colors', sync_files)
        configs['page'] = _load_cached_config('page', sync_files)
        configs['tables'] = _load_cached_config('tables', sync_files)
        configs['notes'] = _load_cached_config('notes', sync_files)
        configs['images'] = _load_cached_config('images', sync_files)
        configs['equations'] = _load_cached_config('equations', sync_files)
        configs['units'] = _load_cached_config('units/units', sync_files)
        configs['report'] = _load_cached_config('report', sync_files)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Warning: Could not load some configuration files: {e}")
        configs = {}
    
    return {
        'project_config': setup_config,
        'configs': configs,
        'layout': layout_name,
        'sync_files': sync_files
    }


def setup_project(layout_name=None, sync_files=True):
    """Setup project with layout and configuration.
    
    Args:
        layout_name: Layout to use
        sync_files: Whether to sync configuration files
        
    Returns:
        Setup result dictionary
    """
    return setup_library_core(layout_name=layout_name, sync_files=sync_files)


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


class ContentProcessor:
    """Content processing utilities for protecting special content during transformations."""
    
    @staticmethod
    def protect_callouts_from_header_processing(content: str) -> Tuple[str, Dict[str, str]]:
        """Protect Quarto callouts from being processed as headers.
        
        Args:
            content: The markdown content to process
            
        Returns:
            Tuple of (protected_content, callout_replacements)
        """
        if not content:
            return content, {}
            
        # Pattern to match Quarto callouts like ::: {.callout-note} or ::: {.content-block}
        callout_pattern = r'(:::?\s*\{[^}]*\}.*?:::?)'
        
        callout_replacements = {}
        counter = 0
        
        def replace_callout(match):
            nonlocal counter
            placeholder = f"__CALLOUT_PLACEHOLDER_{counter}__"
            callout_replacements[placeholder] = match.group(1)
            counter += 1
            return placeholder
            
        # Replace callouts with placeholders
        protected_content = re.sub(callout_pattern, replace_callout, content, flags=re.DOTALL)
        
        return protected_content, callout_replacements
    
    @staticmethod
    def restore_callouts_after_processing(content: str, callout_replacements: Dict[str, str]) -> str:
        """Restore callouts after processing is complete.
        
        Args:
            content: The processed content with placeholders
            callout_replacements: Dictionary mapping placeholders to original callouts
            
        Returns:
            Content with callouts restored
        """
        if not callout_replacements:
            return content
            
        restored_content = content
        for placeholder, original_callout in callout_replacements.items():
            restored_content = restored_content.replace(placeholder, original_callout)
            
        return restored_content


__all__ = [
    'load_setup_config',
    'get_output_directories', 
    'get_absolute_output_directories',
    '_load_cached_config',
    'setup_library_core',
    'setup_project',
    'get_current_project_config',
    'ProjectConfig',
    'ProjectSettings',
    'ContentProcessor'
]
