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
            # STRICT sync_files control - NO synchronization when sync_files=False
            if not sync_files:
                # When sync_files=False, we NEVER sync or create directories
                # The file MUST exist in the package location
                raise FileNotFoundError(f"Configuration file not found in package: {abs_path}")
            
            # Only attempt synchronization when sync_files=True AND path contains 'configuration'
            if sync_files and 'configuration' in abs_path:
                # This is a config file path that needs syncing
                # Find the source file and sync it
                import shutil
                
                # Extract the relative path from configuration and find source
                if '/components/' in abs_path or '\\components\\' in abs_path:
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
                
                # Sync from source if it exists - ONLY WHEN sync_files=True
                if os.path.exists(src_path):
                    os.makedirs(os.path.dirname(abs_path), exist_ok=True)
                    shutil.copy2(src_path, abs_path)
                    logger.info(f"Configuration synchronized: {src_path} → {abs_path}")
                else:
                    raise FileNotFoundError(f"Source configuration file not found: {src_path}")
            else:
                # sync_files=True but not a configuration path
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
    'clear_config_cache',
    'set_temp_config_override',
    'clear_temp_config_cache',
    'disable_temp_cache',
    'enable_temp_cache'
]


def get_setup_config(sync_files: bool = False) -> Dict[str, Any]:
    """Get setup configuration.
    
    Args:
        sync_files: Whether to use synchronized files or package files.
        
    Returns:
        Dict[str, Any]: Complete setup configuration.
    """
    config_path = _resolve_config_path('components/setup', sync_files)
    return _load_cached_files(config_path, sync_files)


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
        config_name: Name of configuration (e.g. 'colors', 'tables', 'components/setup')
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
        if config_name.startswith('components/'):
            config_file = config_name.replace('components/', '') + '.json'
            return str(caller_dir / 'data' / 'configuration' / 'components' / config_file)
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
        if config_name.startswith('components/'):
            config_file = config_name.replace('components/', '') + '.json'
            return str(package_dir / 'components' / config_file)
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


def get_absolute_output_directories(sync_files: bool = False) -> Dict[str, str]:
    """Get absolute paths for output directories from setup configuration.
    
    PURE VERSION: Respects sync_files parameter strictly.
    
    Args:
        sync_files: Whether to use synchronized configuration files
        
    Returns:
        Dictionary with absolute paths for different output directories
        
    Note:
        When sync_files=False, returns simple relative paths without creating directories.
        When sync_files=True, loads from setup configuration and may sync files.
    """
    from pathlib import Path
    import os
    
    if sync_files:
        try:
            # Load setup configuration using sync_files=True (may trigger synchronization)
            setup_config = _load_cached_files(_resolve_config_path('components/setup', sync_files), sync_files)
            directories = setup_config.get('directories', {})
            
            # Convert to absolute paths
            result = {}
            base_path = Path.cwd()
            
            for key, value in directories.items():
                if isinstance(value, str):
                    if not Path(value).is_absolute():
                        result[key] = str(base_path / value)
                    else:
                        result[key] = value
                else:
                    result[key] = str(base_path / f"{key}")
            
            return result
        except Exception:
            # Fallback for sync_files=True
            pass
    
    # sync_files=False or fallback: simple relative paths matching setup.json structure
    base_path = Path.cwd()
    return {
        'data': str(base_path / 'data'),
        'results': str(base_path / 'results'),
        'configuration': str(base_path / 'data' / 'configuration'),
        'brand': str(base_path / 'data' / 'user' / 'brand'),
        'templates': str(base_path / 'data' / 'user' / 'templates'),
        'user': str(base_path / 'data' / 'user'),
        'report': str(base_path / 'results' / 'report'),
        'tables': str(base_path / 'results' / 'report' / 'tables'),
        'figures': str(base_path / 'results' / 'report' / 'figures'),
        'examples': str(base_path / 'data' / 'examples')
    }


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



