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
    """Clear all configuration cache - delegated to data module."""
    from ePy_docs.internals.data_processing._data import clear_config_cache as data_clear_cache
    data_clear_cache()

def set_temp_config_override(config_type: str, key: str, value: Any) -> None:
    """Set a temporary configuration override in memory - delegated to data module."""
    from ePy_docs.internals.data_processing._data import set_temp_config_override as data_set_temp_override
    data_set_temp_override(config_type, key, value)

def clear_temp_config_cache(config_type: str = None) -> None:
    """Clear temporary configuration cache - delegated to data module."""
    from ePy_docs.internals.data_processing._data import clear_temp_config_cache as data_clear_temp_cache
    data_clear_temp_cache(config_type)

def disable_temp_cache() -> None:
    """Disable temporary cache (for testing) - delegated to data module."""
    from ePy_docs.internals.data_processing._data import disable_temp_cache as data_disable_temp_cache
    data_disable_temp_cache()

def enable_temp_cache() -> None:
    """Enable temporary cache - delegated to data module."""
    from ePy_docs.internals.data_processing._data import enable_temp_cache as data_enable_temp_cache
    data_enable_temp_cache()

# Using centralized configuration system
__all__ = [
    '_load_cached_files',
    '_resolve_config_path',
    'clear_config_cache',
    'set_temp_config_override',
    'clear_temp_config_cache',
    'disable_temp_cache',
    'enable_temp_cache',
    'get_config_section',
    '_load_cached_config',
    'get_setup_config'
]


def get_config_section(config_name: str) -> Dict[str, Any]:
    """Get a specific configuration section from ConfigManager.
    
    Args:
        config_name: Name of the configuration section (e.g., 'tables', 'text', 'colors')
        
    Returns:
        Dict with the configuration data for that section
    """
    from ePy_docs.config.config_manager import ConfigManager
    cm = ConfigManager()
    return cm.get_config(config_name)


def _load_cached_config(config_name: str) -> Dict[str, Any]:
    """Load cached configuration using ConfigManager.
    
    This is an alias for get_config_section for backward compatibility.
    
    Args:
        config_name: Name of the configuration section
        
    Returns:
        Dict with the configuration data
    """
    return get_config_section(config_name)


def get_setup_config() -> Dict[str, Any]:
    """Get setup configuration for backward compatibility.
    
    Returns:
        Dict with setup configuration including report_config
    """
    from ePy_docs.config.config_manager import ConfigManager
    cm = ConfigManager()
    
    # Get general config which contains common settings
    general_config = cm.get_config('general')
    
    # Create setup config structure for backward compatibility
    setup_config = {
        'report_config': {
            'project_title': general_config.get('common', {}).get('project', {}).get('name', 'Default Project'),
            'sync_files': False  # Default value
        }
    }
    
    return setup_config


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

def _resolve_config_path(config_name: str) -> str:
    """Resolve configuration path to package resources.
    
    Args:
        config_name: Name of configuration (e.g. 'colors', 'tables', 'components/setup')
        
    Returns:
        Full path to the configuration file alongside the corresponding module
    """
    import os
    from pathlib import Path
    
    package_dir = Path(__file__).parent.parent
    
    # Mapa de configuraciones a sus ubicaciones de módulo
    config_map = {
        # Formatting configs
        'components/tables': 'internals/formatting/tables.epyson',
        'components/text': 'internals/formatting/text.epyson',
        'components/notes': 'internals/formatting/notes.epyson',
        'components/images': 'internals/formatting/images.epyson',
        'components/format': 'internals/formatting/format.epyson',
        'components/code': 'internals/formatting/code.epyson',
        'components/mapper': 'internals/formatting/mapper.epyson',
        # Generation configs
        'components/html': 'internals/generation/html.epyson',
        'components/pdf': 'internals/generation/pdf.epyson',
        'components/references': 'internals/generation/references.epyson',
        'components/paper': 'internals/generation/paper.epyson',
        'components/pages': 'internals/generation/pages.epyson',
        # Styling configs
        'colors': 'internals/styling/colors.epyson',
        'components/colors': 'internals/styling/colors.epyson',  # Alias
        # Root level configs
        'components/report': 'report.epyson',
        # Format config (quarto generation)
        'format': 'internals/generation/format.epyson',
        # Aliases comunes
        'pages': 'internals/generation/pages.epyson',
        'paper': 'internals/generation/paper.epyson',
        'report': 'report.epyson',
        'text': 'internals/formatting/text.epyson',  # Alias para components/text
    }
    
    # Buscar en el mapa
    if config_name in config_map:
        return str(package_dir / config_map[config_name])
    
    # Fallback para configs antiguos en components/
    if config_name.startswith('components/'):
        config_file = config_name.replace('components/', '') + '.json'
        # Intentar en internals/formatting primero
        formatting_path = package_dir / 'internals' / 'formatting' / config_file
        if formatting_path.exists():
            return str(formatting_path)
        # Luego en internals/generation
        generation_path = package_dir / 'internals' / 'generation' / config_file
        if generation_path.exists():
            return str(generation_path)
    
    # Fallback genérico (para compatibilidad)
    return str(package_dir / 'resources' / 'configs' / f'{config_name}.json')


def get_absolute_output_directories(document_type: str) -> Dict[str, str]:
    """Get absolute paths for output directories.
    
    Args:
        document_type: Type of document ("report" or "paper") to determine correct paths
        
    Returns:
        Dictionary with absolute paths for different output directories
    """
    from pathlib import Path
    import os
    
    # Simple relative paths matching setup.json structure
    # Select correct tables/figures directories based on document type
    base_path = Path.cwd()
    
    if document_type == "paper":
        tables_dir = Path('results') / 'paper' / 'tables'
        figures_dir = Path('results') / 'paper' / 'figures'
        output_dir = Path('results') / 'paper'
    else:  # document_type == "report" or fallback
        tables_dir = Path('results') / 'report' / 'tables'
        figures_dir = Path('results') / 'report' / 'figures'
        output_dir = Path('results') / 'report'
    
    return {
        'data': str(base_path / 'data'),
        'results': str(base_path / 'results'),
        'configuration': str(base_path / 'data' / 'configuration'),
        'brand': str(base_path / 'data' / 'user' / 'brand'),
        'templates': str(base_path / 'data' / 'user' / 'templates'),
        'user': str(base_path / 'data' / 'user'),
        'report': str(base_path / 'results' / 'report'),
        'paper': str(base_path / 'results' / 'paper'),
        'examples': str(base_path / 'data' / 'examples'),
        # Document-specific directories (active based on document_type)
        'tables': str(base_path / tables_dir),
        'figures': str(base_path / figures_dir),
        'output': str(base_path / output_dir),
        # All specific table and figure directories (for direct access)
        'tables_report': str(base_path / 'results' / 'report' / 'tables'),
        'figures_report': str(base_path / 'results' / 'report' / 'figures'),
        'tables_paper': str(base_path / 'results' / 'paper' / 'tables'),
        'figures_paper': str(base_path / 'results' / 'paper' / 'figures')
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
    
    def __init__(self):
        # Default settings with sync_files=False for backward compatibility
        self.settings = type('Settings', (), {'sync_files': False})()


def get_current_project_config() -> ProjectConfig:
    """Get current project configuration.
    
    Returns a minimal configuration object for backward compatibility.
    """
    return ProjectConfig()



