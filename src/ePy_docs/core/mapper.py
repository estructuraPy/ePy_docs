"""Column mapping utilities for Robot Structural Analysis data."""

import os
from typing import Optional
from ePy_docs.files.reader import ReadFiles
from ePy_docs.files.data import _load_cached_json

class DataFrameColumnMapper:
    """Utility class for mapping column names using JSON configuration.
    
    Assumptions:
        JSON mapping file contains structured column mapping data organized by element type.
        Default mapping file location follows standard template directory structure.
        Column matching is performed using case-insensitive string containment.
    """
    
    def __init__(self, mapping_file_path: Optional[str] = None):
        """Initialize with column mapping configuration.
        
        Args:
            mapping_file_path: Path to JSON file containing column mappings.
            
        Assumptions:
            If no path provided, uses mapper.json in the same directory as this module.
            Falls back to package directory if templates location not found.
        """
        if mapping_file_path is None:
            # Use mapper.json in the same directory as this module
            current_dir = os.path.dirname(os.path.abspath(__file__))
            self.mapping_file_path = os.path.join(current_dir, 'mapper.json')
        else:
            self.mapping_file_path = mapping_file_path
        
        self._load_cached_json()

    def _load_cached_json(self):
        """Load column mapping from JSON file using cached data.
        
        Raises:
            FileNotFoundError: If mapping file cannot be loaded.
            
        Assumptions:
            JSON file contains valid mapping structure.
            Caching uses absolute file path as key to handle relative path variations.
        """
        if self.mapping_file_path is None:
            raise FileNotFoundError("No mapping file path provided")
        
        self.column_mapping = _load_cached_json(self.mapping_file_path)

    def get_column_type(self, column_name: str, element_type: str) -> Optional[str]:
        """Get standardized column type using JSON mapping configuration.
        
        Args:
            column_name: Original column name from CSV.
            element_type: Type of structural element for mapping lookup.
            
        Returns:
            Standardized column type if pattern match found, None otherwise.
            
        Assumptions:
            Column matching uses uppercase conversion for case-insensitive comparison.
            First matching pattern in mapping dictionary is returned.
            Element type exists as key in loaded mapping configuration.
        """
        col_str = column_name.upper()
        element_mapping = self.column_mapping.get(element_type, {})
        
        for pattern, standard_name in element_mapping.items():
            if pattern in col_str:
                return standard_name
        
        return None
