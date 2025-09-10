"""Setup and configuration utilities for ePy_docs.

Portal de configuración que delega al mundo FILES como fuente de verdad.
Manejo de overrides temporales y resolución de rutas de configuración.
"""

import os
import json
import re
import logging
from pathlib import Path
from typing import Dict, Any, Tuple, Union, List

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

def clear_config_cache():
    """Clear all configuration cache - delegated to FILES world as source of truth."""
    from ePy_docs.files.data import clear_config_cache as files_clear_cache
    files_clear_cache()

def set_temp_config_override(config_type: str, key: str, value: Any) -> None:
    """Set a temporary configuration override in memory - delegated to FILES world."""
    from ePy_docs.files.data import set_temp_config_override as files_set_temp_override
    files_set_temp_override(config_type, key, value)

def clear_temp_config_cache(config_type: str = None) -> None:
    """Clear temporary configuration cache - delegated to FILES world."""
    from ePy_docs.files.data import clear_temp_config_cache as files_clear_temp_cache
    files_clear_temp_cache(config_type)

def disable_temp_cache() -> None:
    """Disable temporary cache (for testing) - delegated to FILES world."""
    from ePy_docs.files.data import disable_temp_cache as files_disable_temp_cache
    files_disable_temp_cache()

def enable_temp_cache() -> None:
    """Enable temporary cache - delegated to FILES world."""
    from ePy_docs.files.data import enable_temp_cache as files_enable_temp_cache
    files_enable_temp_cache()

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
    from ePy_docs.files import _load_cached_files
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
            from ePy_docs.files import _load_cached_files
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



