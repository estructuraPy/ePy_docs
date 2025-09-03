"""Setup and configuration utilities for ePy_docs.

Clean configuration loading from setup.json without fallbacks or hardcoded paths.
Centralized file caching system with strict sync_files control.
NO VERBOSE, NO FALLBACKS, NO HARDCODED PATHS.
"""

import os
import json
import re
import logging
from pathlib import Path
from typing import Dict, Any, Tuple, Union, List

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

_CONFIG_CACHE: Dict[str, Any] = {}

def clear_config_cache():
    """Clear all configuration cache - useful when changing directories or reloading configs."""
    global _CONFIG_CACHE
    _CONFIG_CACHE.clear()

def _load_cached_files(file_path: str, sync_files: bool = False) -> Dict[str, Any]:
    """Load JSON file with optimized caching and strict sync_files control.
    
    Args:
        file_path: Absolute path to the JSON file.
        sync_files: If True, forces reload from disk and updates the cache.
                   If False, uses cache when available and never synchronizes.
        
    Returns:
        Dictionary containing the parsed JSON data.
        
    Raises:
        FileNotFoundError: If the specified file does not exist.
        json.JSONDecodeError: If the file contains invalid JSON.
        PermissionError: If the file cannot be accessed due to permissions.
        RuntimeError: For other file reading errors.
        
    Note:
        When sync_files=False, NO synchronization occurs and cache is preferred.
        When sync_files=True, file is reloaded and cache is updated.
    """
    try:
        abs_path = str(Path(file_path).resolve())
        cache_key = f"json_{abs_path}"

        if not sync_files and cache_key in _CONFIG_CACHE:
            return _CONFIG_CACHE[cache_key]
        
        if not os.path.exists(abs_path):
            # Handle synchronization if needed
            if sync_files and 'configuration' in abs_path:
                # This is a config file path that needs syncing
                # Find the source file and sync it
                import shutil
                
                # Extract the relative path from configuration and find source
                if '/components/' in abs_path or '\\components\\' in abs_path:
                    filename = os.path.basename(abs_path)
                    src_path = os.path.join(os.path.dirname(__file__), '..', 'components', filename)
                elif '/core/' in abs_path or '\\core\\' in abs_path:
                    filename = os.path.basename(abs_path) 
                    src_path = os.path.join(os.path.dirname(__file__), filename)
                elif '/units/' in abs_path or '\\units\\' in abs_path:
                    filename = os.path.basename(abs_path)
                    src_path = os.path.join(os.path.dirname(__file__), '..', 'units', filename)
                elif '/files/' in abs_path or '\\files\\' in abs_path:
                    filename = os.path.basename(abs_path)
                    src_path = os.path.join(os.path.dirname(__file__), '..', 'files', filename)
                elif '/project/' in abs_path or '\\project\\' in abs_path:
                    filename = os.path.basename(abs_path)
                    src_path = os.path.join(os.path.dirname(__file__), '..', 'project', filename)
                else:
                    raise FileNotFoundError(f"Configuration file not found and cannot determine source: {abs_path}")
                
                # Sync from source if it exists
                if os.path.exists(src_path):
                    os.makedirs(os.path.dirname(abs_path), exist_ok=True)
                    shutil.copy2(src_path, abs_path)
                    logger.info(f"Configuration synchronized: {src_path} → {abs_path}")
                else:
                    raise FileNotFoundError(f"Source configuration file not found: {src_path}")
            else:
                raise FileNotFoundError(f"Configuration file not found: {abs_path}")
            
        if not os.path.isfile(abs_path):
            raise ValueError(f"Path is not a file: {abs_path}")
            
        # Read and parse JSON
        with open(abs_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        if not isinstance(data, dict):
            raise ValueError(f"Invalid configuration: {abs_path} does not contain a JSON object")
            
        # Cache the data for future use (always cache when loaded successfully)
        _CONFIG_CACHE[cache_key] = data
            
        return data
        
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in {file_path}: {str(e)}")
        raise
    except FileNotFoundError:
        #  System: No error log for missing optional config files
        raise
    except Exception as e:
        logger.error(f"Error loading {file_path}: {str(e)}")
        raise

# Clean centralized configuration system - NO FALLBACKS, NO VERBOSE, NO HARDCODED
__all__ = [
    '_load_cached_files',
    'get_filepath',
    'get_color',
    'clear_config_cache',
    'get_absolute_output_directories',
    'ContentProcessor',
    'ProjectConfig',
    'get_current_project_config'
]

def get_absolute_output_directories(sync_files: bool = False) -> Dict[str, str]:
    """Get absolute paths for output directories.
    
    Args:
        sync_files: Whether to use external data configuration
        
    Returns:
        Dictionary with absolute paths for output directories
    """
    import os
    from pathlib import Path
    
    current_dir = Path.cwd()
    
    # Load directories from setup.json - NO HARDCODED VALUES
    try:
        # setup.json is in the core directory, use direct path
        setup_config_path = Path(__file__).parent / 'setup.json'
        setup_config = _load_cached_files(str(setup_config_path), sync_files)
        
        # Extract directories from setup.json
        if 'directories' in setup_config:
            output_dirs = {}
            for dir_name, relative_path in setup_config['directories'].items():
                output_dirs[dir_name] = str(current_dir / relative_path)
        else:
            raise ValueError("No 'directories' section found in setup.json")
            
    except Exception as e:
        raise ValueError(f"Failed to load directories from setup.json: {e}. Please ensure setup.json is properly configured.")
    
    # Create directories if they don't exist (respecting sync_files setting)
    for dir_name, dir_path in output_dirs.items():
        # Skip configuration directory when sync_files=False
        if not sync_files and dir_name == 'configuration':
            continue
        os.makedirs(dir_path, exist_ok=True)
    
    return output_dirs


def _get_caller_directory() -> Path:
    """Get the directory of the script/notebook that called the library.
    
    Uses the call stack to find the first frame outside of ePy_docs package.
    This allows automatic detection of the user's working directory.
    
    Returns:
        Path to the directory containing the calling script/notebook
    """
    import inspect
    from pathlib import Path
    
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

def get_filepath(config_key: str, sync_files: bool = False) -> str:
    """Get filepath from setup.json configuration - NO HARDCODED PATHS.
    
    Args:
        config_key: Key path to the file in setup.json (e.g. 'configuration.styling.colors_json')
        sync_files: If True, uses data/configuration structure. If False, uses package structure.
        
    Returns:
        Absolute path to the requested file.
        
    Raises:
        KeyError: If config_key not found in setup.json
        FileNotFoundError: If setup.json not found
    """
    from pathlib import Path
    
    # Load setup.json from package directory - this is the ONLY hardcoded path allowed
    package_dir = Path(__file__).parent
    setup_path = package_dir / 'setup.json'
    setup_config = _load_cached_files(str(setup_path), sync_files=False)
    
    # Parse the config key path (e.g., 'configuration.styling.colors_json')
    keys = config_key.split('.')
    value = setup_config
    
    for key in keys:
        if key not in value:
            raise KeyError(f"Configuration key '{config_key}' not found in setup.json")
        value = value[key]
    
    if not isinstance(value, str):
        raise ValueError(f"Configuration key '{config_key}' must point to a string filepath")
    
    # Determine base directory
    if sync_files:
        base_dir = _get_caller_directory()
        config_base = base_dir / 'data' / 'configuration'
    else:
        base_dir = Path(__file__).parent.parent
        config_base = base_dir
    
    # Resolve the full path
    full_path = config_base / value
    return str(full_path.resolve())

def _resolve_config_path(config_name: str, sync_files: bool = False) -> str:
    """DEPRECATED: Legacy function for backward compatibility.
    Use get_filepath() instead with proper config keys from setup.json.
    """
    # Special case for core/setup - return the setup.json file itself
    if config_name == 'core/setup':
        from pathlib import Path
        return str(Path(__file__).parent / 'setup.json')
    
    # PURIFIED: NO hardcoded mappings - Lord Supremo demands direct _load_cached_files usage
    raise ValueError(f"Legacy config access forbidden: {config_name}. Use _load_cached_files with get_filepath() directly.")


class ContentProcessor:
    """Content processing utilities for callout protection and text manipulation."""
    
    @staticmethod
    def protect_callouts_from_header_processing(content: str):
        """Protect Quarto callouts from header processing.
        
        Args:
            content: Raw content string
            
        Returns:
            Tuple of (protected_content, callout_replacements)
        """
        import re
        
        # Find all callout blocks
        callout_pattern = r':::\{([^}]*)\}\s*\n(.*?)\n:::'
        callouts = re.findall(callout_pattern, content, re.DOTALL)
        
        # Create replacement tokens
        replacements = {}
        protected_content = content
        
        for i, (callout_type, callout_content) in enumerate(callouts):
            token = f"__CALLOUT_PROTECTED_{i}__"
            original_callout = f":::{{{callout_type}}}\n{callout_content}\n:::"
            replacements[token] = original_callout
            protected_content = protected_content.replace(original_callout, token, 1)
        
        return protected_content, replacements
    
    @staticmethod
    def restore_callouts_after_processing(content: str, callout_replacements: dict):
        """Restore protected callouts after processing.
        
        Args:
            content: Content with protected callout tokens
            callout_replacements: Dictionary mapping tokens to original callouts
            
        Returns:
            Content with callouts restored
        """
        restored_content = content
        
        for token, original_callout in callout_replacements.items():
            restored_content = restored_content.replace(token, original_callout)
        
        return restored_content


class ProjectConfig:
    """Project configuration wrapper for backward compatibility."""
    
    def __init__(self, sync_files: bool = False):
        self.settings = type('Settings', (), {'sync_files': sync_files})()


def get_current_project_config() -> ProjectConfig:
    """Get current project configuration.
    
    Returns a minimal configuration object for backward compatibility.
    This function provides a default sync_files=False setting.
    """
    return ProjectConfig(sync_files=False)
