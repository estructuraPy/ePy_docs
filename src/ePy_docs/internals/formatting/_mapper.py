"""Column mapping utilities for Robot Structural Analysis data.

Pure functions for column mapping without class overhead.
TRANSPARENCY DIMENSION: Pure functions, no class state, direct operations.
"""

import os
from typing import Optional, Dict, Any
from ePy_docs.internals.data_processing._data import load_cached_files


# GLOBAL MAPPING CACHE - SINGLETON PATTERN
_GLOBAL_MAPPING_CACHE = {
    'loaded_mappings': {},
    'default_mapping_path': None
}


def initialize_default_mapping_path() -> None:
    """Initialize default mapping file path.
    
    Sets the default path to mapper.json in the same directory as this module.
    """
    global _GLOBAL_MAPPING_CACHE
    current_dir = os.path.dirname(os.path.abspath(__file__))
    _GLOBAL_MAPPING_CACHE['default_mapping_path'] = os.path.join(current_dir, 'mapper.json')


def load_mapping_config(mapping_file_path: Optional[str] = None) -> Dict[str, Any]:
    """Load column mapping configuration from JSON file.
    
    Args:
        mapping_file_path: Path to JSON file. Uses default if None.
        
    Returns:
        Column mapping configuration dictionary
        
    Raises:
        FileNotFoundError: If mapping file cannot be loaded
    """
    global _GLOBAL_MAPPING_CACHE
    
    # Use default path if none provided
    if mapping_file_path is None:
        if _GLOBAL_MAPPING_CACHE['default_mapping_path'] is None:
            initialize_default_mapping_path()
        mapping_file_path = _GLOBAL_MAPPING_CACHE['default_mapping_path']
    
    if mapping_file_path is None:
        raise FileNotFoundError("No mapping file path provided")
    
    # Check cache first
    if mapping_file_path in _GLOBAL_MAPPING_CACHE['loaded_mappings']:
        return _GLOBAL_MAPPING_CACHE['loaded_mappings'][mapping_file_path]
    
    # Load and cache mapping
    mapping_config = load_cached_files(mapping_file_path)
    _GLOBAL_MAPPING_CACHE['loaded_mappings'][mapping_file_path] = mapping_config
    
    return mapping_config


def get_column_type(column_name: str, element_type: str, 
                   mapping_file_path: Optional[str] = None) -> Optional[str]:
    """Get standardized column type using JSON mapping configuration.
    
    Args:
        column_name: Original column name from CSV
        element_type: Type of structural element for mapping lookup
        mapping_file_path: Path to mapping file. Uses default if None.
        
    Returns:
        Standardized column type if pattern match found, None otherwise
    """
    mapping_config = load_mapping_config(mapping_file_path)
    
    col_str = column_name.upper()
    element_mapping = mapping_config.get(element_type, {})
    
    for pattern, standard_name in element_mapping.items():
        if pattern in col_str:
            return standard_name
    
    return None


#
# LEGACY CLASS WRAPPER - TRANSPARENCY DIMENSION COMPLIANCE
# Maintains backward compatibility while encouraging pure function usage
#

class DataFrameColumnMapper:
    """LEGACY CLASS WRAPPER - Use pure functions instead.
    
    This class exists only for backward compatibility.
    All methods delegate to pure functions.
    """
    
    def __init__(self, mapping_file_path: Optional[str] = None):
        """LEGACY CONSTRUCTOR - Use load_mapping_config() function instead."""
        self.mapping_file_path = mapping_file_path
        # Don't load immediately - let pure functions handle it
    
    def _load_mapping_config(self):
        """LEGACY METHOD - Use load_mapping_config() function instead."""
        # This method is no longer needed as loading is handled by pure functions
        pass
    
    def get_column_type(self, column_name: str, element_type: str) -> Optional[str]:
        """LEGACY METHOD - Use get_column_type() function instead."""
        return get_column_type(column_name, element_type, self.mapping_file_path)
