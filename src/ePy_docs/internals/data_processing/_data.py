"""Data processing utilities for ePy_files.

Provides functions for data loading, caching, and transformation to support
various file formats and unit conversion operations.
"""

import os
import re
import json
import logging
from functools import lru_cache
from pathlib import Path
from typing import Dict, Any, List, Optional, Union, Tuple, Set
import pandas as pd
from pandas.api.types import is_numeric_dtype

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global cache for JSON data to avoid redundant file operations
_JSON_DATA_CACHE: Dict[str, Any] = {}
_READER_CONFIG: Optional[Dict[str, Any]] = None

# Cache for configuration files
_CONFIG_CACHE: Dict[str, Any] = {}

# Temporary config cache for overrides (separate from main cache)
_temp_config_cache: Dict[str, Any] = {}
_temp_cache_enabled: bool = True

def clear_config_cache():
    """Clear all configuration cache - useful when changing directories or reloading configs."""
    global _CONFIG_CACHE, _READER_CONFIG
    _CONFIG_CACHE.clear()
    _READER_CONFIG = None

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

def get_reader_config() -> Dict[str, Any]:
    """Load and cache reader configuration from epyson file."""
    global _READER_CONFIG
    
    if _READER_CONFIG is None:
        try:
            config_path = Path(__file__).parent / 'reader.epyson'
            _READER_CONFIG = load_cached_files(str(config_path))
            
            # Validate required sections
            required_sections = ['file_paths', 'file_extensions', 'encoding', 'csv_detection']
            for section in required_sections:
                if section not in _READER_CONFIG:
                    raise ValueError(f"Missing required section '{section}' in reader configuration")
                    
        except Exception as e:
            logger.error(f"Failed to load reader configuration: {e}")
            raise
            
    return _READER_CONFIG

def clear_local_config_cache():
    """Clear cache for local configuration files."""
    global _CONFIG_CACHE
    keys_to_remove = [k for k in _CONFIG_CACHE.keys() if "configuration" in k and k.endswith(".json")]
    for key in keys_to_remove:
        del _CONFIG_CACHE[key]


def load_cached_files(file_path: str) -> Dict[str, Any]:
    """Load JSON file with optimized caching.
    
    Args:
        file_path: Absolute path to the JSON file.
        
    Returns:
        Dictionary containing the parsed JSON data.
        
    Raises:
        FileNotFoundError: If the specified file does not exist.
        json.JSONDecodeError: If the file contains invalid JSON.
        PermissionError: If the file cannot be accessed due to permissions.
        RuntimeError: For other file reading errors.
    """
    abs_path = str(Path(file_path).resolve())
    cache_key = f"json_{abs_path}"

    # Always check cache first
    if cache_key in _CONFIG_CACHE:
        return _CONFIG_CACHE[cache_key]
    
    if not os.path.exists(abs_path):
        # The file MUST exist in the package location (resources/configs/)
        raise FileNotFoundError(f"Configuration file not found in package: {abs_path}")
        
    if not os.path.isfile(abs_path):
        raise ValueError(f"Path is not a file: {abs_path}")
        
    # Read and parse JSON
    with open(abs_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    if not isinstance(data, dict):
        raise ValueError(f"Invalid configuration: {abs_path} does not contain a JSON object")
        
    # Cache the data for future use (always cache when loaded successfully)
    _CONFIG_CACHE[cache_key] = data
    
    # Apply temporary config overrides if enabled
    if _temp_cache_enabled and _temp_config_cache:
        # Extract config type from file path for temp overrides
        config_type = None
        filename = os.path.basename(abs_path)
        if filename.startswith(('report', 'Report')):
            config_type = 'report'
        elif filename.startswith(('page', 'Page')):
            config_type = 'page'
        elif filename.startswith(('table', 'Table')):
            config_type = 'table'
        elif filename.startswith(('format', 'Format')):
            config_type = 'format'
        
        # Apply overrides if config type found
        if config_type and config_type in _temp_config_cache:
            data = data.copy()  # Create copy to avoid modifying cached original
            data.update(_temp_config_cache[config_type])
        
    return data




def _safe_get_nested(data: Dict[str, Any], path: str, default: Any = None) -> Any:
    """Safely get a nested value from a dictionary using dot notation.
    
    Args:
        data: Dictionary to access. Must be a dictionary.
        path: Dot-separated path to nested value (e.g., 'section.subsection.key').
        default: Value to return if path is not found or invalid.
        
    Returns:
        The value at the specified path or the default value if not found.
        
    Example:
        >>> data = {'a': {'b': {'c': 42}}}
        >>> _safe_get_nested(data, 'a.b.c')
        42
        >>> _safe_get_nested(data, 'a.b.x', default=0)
        0
    """
    if not isinstance(data, dict):
        logger.debug(f"Expected dict, got {type(data).__name__}")
        return default
        
    if not path or not isinstance(path, str):
        return default
        
    try:
        result = data
        for key in path.split('.'):
            if not isinstance(result, dict):
                return default
            result = result.get(key, default)
        return result
    except (AttributeError, TypeError) as e:
        logger.debug(f"Error accessing path '{path}': {e}")
        return default


def safe_parse_numeric(value: Any) -> float:
    """Parse a value to float using configuration from reader.json.
    
    Args:
        value: Value to parse (str, int, float, etc.)
        
    Returns:
        Parsed float value
        
    Raises:
        ValueError: If the value cannot be parsed as a number
    """
    if value is None or pd.isna(value):
        raise ValueError("Cannot parse None or NaN value")

    # Get configuration
    config = get_reader_config()
    
    # Try specific numeric_parsing config first, fallback to csv_detection
    numeric_config = _safe_get_nested(config, 'numeric_parsing', {})
    csv_config = _safe_get_nested(config, 'csv_detection', {})
    
    # Get non-numeric patterns from config
    non_numeric_patterns = set(
        pattern.lower() 
        for pattern in _safe_get_nested(numeric_config, 'non_numeric_patterns', 
                                       _safe_get_nested(config, 'non_numeric_patterns', [
                                           'nan', 'n/a', 'none', 'null', 'unknown', 'totals'
                                       ]))
    )
    
    # Handle numeric types
    if isinstance(value, (int, float)):
        if pd.isna(value):
            raise ValueError("Cannot parse NaN value")
        return float(value)

    # Convert to string and clean
    str_value = str(value).strip().lower()
    
    # Check against non-numeric patterns
    if any(str_value == pattern or str_value.startswith(f"{pattern} ") 
           for pattern in non_numeric_patterns):
        raise ValueError(f"Non-numeric pattern detected: {value}")

    # Handle empty strings and dashes
    if not str_value or str_value == '-':
        raise ValueError(f"Empty or dash value: {value}")

    # Get decimal and thousand separators from config
    # Priority: numeric_parsing > csv_detection > defaults
    decimal_sep = (_safe_get_nested(numeric_config, 'decimal_separator') or 
                   _safe_get_nested(csv_config, 'decimal_separator', '.'))
    thousand_sep = (_safe_get_nested(numeric_config, 'thousand_separator') or 
                    _safe_get_nested(csv_config, 'thousand_separator', ''))
    
    try:
        # Clean the string based on configuration
        clean_str = str_value
        
        # Remove thousand separators if they match the config
        if thousand_sep:
            clean_str = clean_str.replace(thousand_sep, '')
            
        # Replace decimal separator with standard dot
        if decimal_sep != '.':
            clean_str = clean_str.replace(decimal_sep, '.')
            
        # Final conversion
        return float(clean_str)
        
    except ValueError as e:
        raise ValueError(f"Cannot parse numeric value: {value}") from e


def hide_dataframe_columns(df: pd.DataFrame, 
                         hide_columns: Optional[Union[str, List[str]]] = None) -> pd.DataFrame:
    """Hide columns from a DataFrame based on exact or partial name matching.
    
    Args:
        df: Input DataFrame to process.
        hide_columns: Column name(s) to hide. Can be a single string or a list of strings.
                     If None or empty, returns a copy of the original DataFrame.
                     
    Returns:
        A new DataFrame with specified columns removed.
        
    Raises:
        TypeError: If df is not a pandas DataFrame.
        
    Example:
        >>> df = pd.DataFrame({'A': [1, 2], 'B': [3, 4], 'C': [5, 6]})
        >>> hide_dataframe_columns(df, ['A', 'B'])
           C
        0  5
        1  6
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"Expected pandas DataFrame, got {type(df).__name__}")
    
    if not hide_columns:
        return df.copy()
    
    # Normalize input to list of strings
    columns_to_hide = [hide_columns] if isinstance(hide_columns, str) else list(hide_columns)
    
    # Find columns to keep (case-insensitive match)
    all_columns = set(df.columns)
    hidden_columns = set()
    
    for pattern in columns_to_hide:
        if not isinstance(pattern, str):
            logger.warning(f"Skipping non-string pattern: {pattern}")
            continue
            
        # Exact match
        if pattern in all_columns:
            hidden_columns.add(pattern)
            continue
            
        # Case-insensitive partial match
        pattern_lower = pattern.lower()
        matched = [col for col in all_columns if pattern_lower in col.lower()]
        hidden_columns.update(matched)
    
    # Log hidden columns for debugging
    if hidden_columns:
        logger.debug(f"Hiding columns: {', '.join(sorted(hidden_columns))}")
    
    # Return new DataFrame with only visible columns
    return df[[col for col in df.columns if col not in hidden_columns]].copy()


def process_numeric_columns(df: pd.DataFrame, 
                          id_columns: Optional[List[str]] = None) -> pd.DataFrame:
    """Process DataFrame columns to convert numeric data to appropriate types.
    
    Args:
        df: Input DataFrame to process.
        id_columns: List of column names to treat as identifiers (not converted).
                   If None, no columns are treated as identifiers.
                   
    Returns:
        A new DataFrame with numeric columns converted to appropriate types.
        
    Raises:
        TypeError: If df is not a pandas DataFrame.
        
    Note:
        - Columns in id_columns are never converted.
        - Only attempts conversion if majority of sample values are numeric.
        - Preserves original dtype if conversion fails.
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"Expected pandas DataFrame, got {type(df).__name__}")
    
    id_columns = set(id_columns) if id_columns else set()
    processed_df = df.copy()
    
    # Get configuration
    config = get_reader_config()
    sample_size = _safe_get_nested(config, 'csv_detection.sample_rows', 10)
    numeric_threshold = _safe_get_nested(config, 'csv_detection.numeric_threshold', 0.5)
    
    for col in processed_df.columns:
        if col in id_columns or processed_df[col].empty:
            continue
            
        # Skip if already numeric
        if is_numeric_dtype(processed_df[col]):
            continue
            
        # Only process object/string columns
        if processed_df[col].dtype != 'object':
            continue
            
        # Check sample of non-null values
        non_null = processed_df[col].dropna()
        if non_null.empty:
            continue
            
        sample = non_null.head(sample_size)
        numeric_count = 0
        
        # Count numeric values in sample
        for val in sample:
            try:
                safe_parse_numeric(val)
                numeric_count += 1
            except ValueError:
                pass
        
        # Only convert if majority of sample is numeric
        if numeric_count / len(sample) >= numeric_threshold:
            try:
                # Replace deprecated errors='ignore' with explicit exception handling
                processed_df[col] = pd.to_numeric(processed_df[col])
                if not is_numeric_dtype(processed_df[col]):
                    logger.debug(f"Could not convert column '{col}' to numeric")
            except (ValueError, TypeError) as e:
                # Handle conversion errors explicitly instead of using errors='ignore'
                logger.debug(f"Column '{col}' contains non-numeric values, keeping as original type: {e}")
            except Exception as e:
                logger.debug(f"Error converting column '{col}': {e}")
    
    return processed_df



def sort_dataframe_rows(df: pd.DataFrame, sort_by: Union[str, Tuple[str, str], List[Union[str, Tuple[str, str]]]]) -> pd.DataFrame:
    """Sort DataFrame rows by column(s) with strict syntax validation.
    
    Pure sorting operation with halt-on-failure enforcement.
    No verbose output, no fallback contamination.
    
    Args:
        df: DataFrame to sort
        sort_by: Sort conditions. Can be:
                - Single column name: "Column" (ascending by default)
                - Single tuple: ("Column", "asc"/"desc")
                - List of column names: ["Col1", "Col2"] (all ascending)
                - List of tuples: [("Col1", "asc"), ("Col2", "desc")]
                - Mixed list: ["Col1", ("Col2", "desc")]
        
    Returns:
        Sorted DataFrame
        
    Raises:
        ValueError: If sort_by format is invalid or columns don't exist
        
    Examples:
        sort_by="Node"
        sort_by=("Load_kN", "desc")
        sort_by=["Zone", "Node"]
        sort_by=[("Zone", "asc"), ("Load_kN", "desc"), "Node"]
    """
    if sort_by is None:
        return df.copy()
    
    # Normalize input to list of tuples - halt on invalid input
    if isinstance(sort_by, str):
        sort_conditions = [(sort_by, 'asc')]
    elif isinstance(sort_by, tuple):
        sort_conditions = [sort_by]
    elif isinstance(sort_by, list):
        sort_conditions = []
        for item in sort_by:
            if isinstance(item, str):
                sort_conditions.append((item, 'asc'))
            elif isinstance(item, tuple):
                sort_conditions.append(item)
            else:
                raise ValueError(f"Invalid sort condition: {item}. Must be string or tuple.")
    else:
        raise ValueError(f"Invalid sort_by format: {type(sort_by)}. Must be string, tuple, or list.")
    
    # Validate columns and directions - halt on errors
    valid_columns = []
    valid_ascending = []
    
    for column_name, direction in sort_conditions:
        if column_name not in df.columns:
            raise ValueError(f"Column '{column_name}' not found in DataFrame")
        
        valid_columns.append(column_name)
        
        # Strict direction validation - no fallbacks
        direction_lower = str(direction).lower()
        if direction_lower in ['asc', 'ascending', 'up', 'true', '1']:
            valid_ascending.append(True)
        elif direction_lower in ['desc', 'descending', 'down', 'false', '0']:
            valid_ascending.append(False)
        else:
            raise ValueError(f"Invalid sort direction '{direction}' for column '{column_name}'. Use 'asc' or 'desc'.")
    
    # Apply sorting - halt on failure
    sorted_df = df.sort_values(
        by=valid_columns, 
        ascending=valid_ascending,
        na_position='last'
    )
    
    # Reset index only for simple RangeIndex
    if isinstance(df.index, pd.RangeIndex):
        sorted_df = sorted_df.reset_index(drop=True)
    
    return sorted_df


def split_large_table(df: pd.DataFrame, max_rows: Union[int, List[int]]) -> List[pd.DataFrame]:
    """Split DataFrame into chunks using pure pandas operations.
    
    Args:
        df: DataFrame to split
        max_rows: Chunk size(s) - int for uniform chunks, list for custom sizes
        
    Returns:
        List of DataFrame chunks
        
    Raises:
        ValueError: If max_rows format is invalid
    """
    total_rows = len(df)
    
    if isinstance(max_rows, (int, float)):
        # Uniform chunks using pure pandas
        chunk_size = int(max_rows)
        if total_rows <= chunk_size:
            return [df]
        return [df.iloc[i:i + chunk_size].copy() for i in range(0, total_rows, chunk_size)]
    
    elif isinstance(max_rows, list):
        if not max_rows:
            return [df]
        
        # Custom chunks using cumulative indices
        import numpy as np
        chunk_sizes = [int(size) for size in max_rows]
        indices = np.cumsum([0] + chunk_sizes)
        
        chunks = []
        for i in range(len(chunk_sizes)):
            start_idx = indices[i]
            end_idx = min(indices[i + 1], total_rows)
            if start_idx >= total_rows:
                break
            chunks.append(df.iloc[start_idx:end_idx].copy())
        
        # Handle remainder
        if indices[len(chunk_sizes)] < total_rows:
            chunks.append(df.iloc[indices[len(chunk_sizes)]:].copy())
        
        return chunks
    
    else:
        raise ValueError(f"max_rows must be int, float, or list of int/float, got {type(max_rows)}")

