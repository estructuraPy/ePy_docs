"""Setup and configuration utilities for ePy_docs.

Clean configuration loading from setup.json without fallbacks or hardcoded paths.
Centralized file caching system with strict sync_files control.
"""

import os
import json
import re
import logging
from pathlib import Path
from typing import Dict, Any, Tuple, Union, List

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

_CONFIG_CACHE: Dict[str, Any] = {}

_temp_config_cache = {}
_temp_cache_enabled = True

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

# Using centralized configuration system
__all__ = [
    '_load_cached_files',
    '_resolve_config_path',
    'get_color',
    'clear_config_cache',
    'set_temp_config_override',
    'clear_temp_config_cache',
    'disable_temp_cache',
    'enable_temp_cache'
]

def get_color(path: str, format_type: str = "rgb", sync_files: bool = True) -> Union[List[int], str]:
    """ PURIFICADO: Delegate to colors.py guardian - NO DIRECT ACCESS TO colors.json!"""
    from ePy_docs.components.colors import get_color_value
    return get_color_value(path, format_type, sync_files)

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
    
    # Default directories structure
    output_dirs = {
        'figures': str(current_dir / 'results' / 'report' / 'figures'),
        'tables': str(current_dir / 'results' / 'report' / 'tables'),
        'report': str(current_dir / 'results' / 'report'),
        'results': str(current_dir / 'results'),
        'data': str(current_dir / 'data'),
        'examples': str(current_dir / 'data' / 'examples'),
        'configuration': str(current_dir / 'data' / 'configuration')
    }
    
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

def _resolve_config_path(config_name: str, sync_files: bool = False) -> str:
    """Resolve configuration path based on sync_files setting.
    
    Args:
        config_name: Name of configuration (e.g. 'colors', 'tables', 'core/setup')
        sync_files: If True, returns path to data/configuration relative to caller directory.
                   If False, returns path to src/ePy_docs package (never creates directories).
        
    Returns:
        Full path to the configuration file
    """
    import os
    from pathlib import Path
    
    # Always use package directory when sync_files=False to avoid creating directories
    package_dir = Path(__file__).parent.parent
    
    if sync_files:
        # Path to data/configuration relative to caller directory (only when explicitly requested)
        caller_dir = _get_caller_directory()
        if config_name.startswith('core/'):
            config_file = config_name.replace('core/', '') + '.json'
            return str(caller_dir / 'data' / 'configuration' / 'core' / config_file)
        elif config_name.startswith('units/'):
            config_file = config_name.replace('units/', '') + '.json'
            return str(caller_dir / 'data' / 'configuration' / 'units' / config_file)
        elif config_name.startswith('files/'):
            config_file = config_name.replace('files/', '') + '.json'
            return str(caller_dir / 'data' / 'configuration' / 'files' / config_file)
        elif config_name.startswith('components/'):
            config_file = config_name.replace('components/', '') + '.json'
            return str(caller_dir / 'data' / 'configuration' / 'components' / config_file)
        else:
            # Default to components
            return str(caller_dir / 'data' / 'configuration' / 'components' / f'{config_name}.json')
    else:
        # Always use package directory when sync_files=False (prevents directory creation)
        if config_name.startswith('core/'):
            config_file = config_name.replace('core/', '') + '.json'
            return str(package_dir / 'core' / config_file)
        elif config_name.startswith('units/'):
            config_file = config_name.replace('units/', '') + '.json'
            return str(package_dir / 'units' / config_file)
        elif config_name.startswith('files/'):
            config_file = config_name.replace('files/', '') + '.json'
            return str(package_dir / 'files' / config_file)
        elif config_name.startswith('components/'):
            config_file = config_name.replace('components/', '') + '.json'
            return str(package_dir / 'components' / config_file)
        else:
            # Default to components
            return str(package_dir / 'components' / f'{config_name}.json')


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
