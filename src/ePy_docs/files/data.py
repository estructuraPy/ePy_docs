"""Data processing utilities for ePy_docs.

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
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# Global cache for JSON data to avoid redundant file operations
_JSON_DATA_CACHE: Dict[str, Any] = {}
_READER_CONFIG: Optional[Dict[str, Any]] = None

def clear_config_cache():
    """Clear all configuration cache - useful when changing directories or reloading configs."""
    # Import here to avoid circular imports
    from ePy_docs.core.setup import clear_config_cache as core_clear_cache
    core_clear_cache()

def get_reader_config() -> Dict[str, Any]:
    """Load and cache reader configuration from JSON using centralized system."""
    global _READER_CONFIG
    
    if _READER_CONFIG is None:
        try:
            # Import here to avoid circular imports
            from ePy_docs.core.setup import _load_cached_files, _resolve_config_path
            config_path = _resolve_config_path('files/reader', sync_files=False)
            _READER_CONFIG = _load_cached_files(config_path, sync_files=False)
            
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
    # Import here to avoid circular imports
    from ePy_docs.core.setup import clear_config_cache
    clear_config_cache()

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
    csv_config = config.get('csv_detection', {})
    
    # Get non-numeric patterns from config
    non_numeric_patterns = set(
        pattern.lower() 
        for pattern in config.get('non_numeric_patterns', [
            'nan', 'n/a', 'none', 'null', 'unknown', 'totals'
        ])
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
    decimal_sep = csv_config.get('decimal_separator', '.')
    thousand_sep = csv_config.get('thousand_separator', '')
    
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
    sample_size = config.get('csv_detection', {}).get('sample_rows', 10)
    numeric_threshold = config.get('csv_detection', {}).get('numeric_threshold', 0.5)
    
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

def convert_dataframe_to_table_with_units(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Convert a DataFrame to table format with comprehensive unit processing and conversion.
    
    This function applies the full unit conversion pipeline including:
    1. Unit detection from column names
    2. Conversion to default/target units via convert_to_default_units
    3. Numeric column processing
    4. Fallback to basic unit detection if full conversion fails
    
    Args:
        df: Input DataFrame
        
    Returns:
        Tuple of (converted_df, conversion_log)
    """
    from ePy_docs.units.units import auto_detect_and_convert_units
    
    # Apply full unit conversion pipeline
    try:
        converted_df, conversion_log = auto_detect_and_convert_units(df)
        
        # Check if conversions were successful
        failed_conversions = []
        successful_conversions = []
        
        for col, log_msg in conversion_log.items():
            if isinstance(log_msg, str):
                if 'error' in log_msg.lower() or 'failed' in log_msg.lower():
                    failed_conversions.append(col)
                else:
                    successful_conversions.append(col)
        
        if failed_conversions:
            # Try to at least detect and preserve unit information for failed conversions
            for col in failed_conversions:
                try:
                    units = extract_units_from_columns(pd.DataFrame(columns=[col]))
                    if col in units:
                        conversion_log[col] = f"Fallback: preserved unit '{units[col]}'"
                except Exception:
                    conversion_log[col] = "Fallback: no unit detected"
        
        # If no unit conversion occurred at all, use the original dataframe
        if not conversion_log or all('error' in str(v) for v in conversion_log.values()):
            converted_df = df.copy()
            conversion_log = {"note": "No unit conversions applied"}
            
    except Exception as e:
        converted_df = df.copy()
        conversion_log = {"error": f"Unit conversion failed: {e}"}
    
    # Process numeric columns to ensure proper formatting
    converted_df = process_numeric_columns(converted_df)
    
    return converted_df, conversion_log

def extract_units_from_columns(df: pd.DataFrame) -> Dict[str, str]:
    """Extract units from column names.
    
    Args:
        df: DataFrame with columns that may contain units
        
    Returns:
        Dictionary mapping column names to their units
    """
    units_dict = {}
    
    for col in df.columns:
        if isinstance(col, str):
            # Look for units in parentheses or brackets
            unit_pattern = r'\[([^\]]+)\]|\(([^\)]+)\)'
            match = re.search(unit_pattern, col)
            
            if match:
                unit = match.group(1) or match.group(2)
                units_dict[col] = unit
    
    return units_dict

def is_summary_row(row: pd.Series) -> bool:
    """Check if a row is a summary row (contains totals, sums, etc.).
    
    Args:
        row: Pandas Series representing a row
        
    Returns:
        True if the row appears to be a summary row
    """
    if row.empty:
        return False
    
    # Convert all values to string for checking
    row_str = row.astype(str).str.lower()
    
    # Check for summary keywords
    summary_keywords = ['total', 'sum', 'totals', 'summary', 'grand total', 'subtotal']
    
    # Check if any cell contains summary keywords
    for keyword in summary_keywords:
        if any(keyword in str(val).lower() for val in row_str):
            return True
    
    return False

def clean_first_column_bom(df: pd.DataFrame) -> pd.DataFrame:
    """Clean BOM (Byte Order Mark) from the first column name.
    
    Args:
        df: DataFrame that might have BOM in first column
        
    Returns:
        DataFrame with cleaned first column name
    """
    if df.empty:
        return df
    
    cleaned_df = df.copy()
    first_col = df.columns[0]
    
    # Remove BOM characters
    if isinstance(first_col, str):
        # Remove common BOM characters
        cleaned_name = first_col.lstrip('\ufeff\ufffe\u0000')
        
        if cleaned_name != first_col:
            cleaned_df = cleaned_df.rename(columns={first_col: cleaned_name})
    
    return cleaned_df

def filter_dataframe_rows(df: pd.DataFrame, filter_by: Union[Tuple[str, Union[str, int, float, List]], List[Tuple[str, Union[str, int, float, List]]]]) -> pd.DataFrame:
    """Filter DataFrame rows by column content using tuples.
    
    Supports both single values and lists of values for convenient filtering.
    
    Args:
        df: DataFrame to filter
        filter_by: Filter conditions. Can be:
                  - Single tuple: (column_name, value) 
                  - Single tuple with list: (column_name, [value1, value2, value3])
                  - List of tuples: [(column_name1, value1), (column_name2, [val2a, val2b]), ...]
        
    Returns:
        Filtered DataFrame
        
    Examples:
        # Single value
        filter_by=("Status", "Active")
        
        # Multiple values for same column (convenient syntax)
        filter_by=("Node", ["1", "2", "3"])  # Equivalent to [("Node", "1"), ("Node", "2"), ("Node", "3")]
        
        # Mixed conditions
        filter_by=[("Zone", "A"), ("Node", ["1", "2", "3"]), ("Status", "Active")]
    """
    if filter_by is None:
        return df.copy()
    
    filtered_df = df.copy()
    
    # Convert single tuple to list for uniform processing
    if isinstance(filter_by, tuple):
        filter_conditions = [filter_by]
    else:
        filter_conditions = filter_by
    
    # Expand any tuples that have lists as values
    expanded_conditions = []
    for column_name, filter_value in filter_conditions:
        if isinstance(filter_value, list):
            # Expand list into individual tuples
            for single_value in filter_value:
                expanded_conditions.append((column_name, single_value))
            print(f"🔄 Expanded filter for '{column_name}': {len(filter_value)} values")
        else:
            # Keep single values as-is
            expanded_conditions.append((column_name, filter_value))
    
    # Group conditions by column for proper OR logic within same column
    column_conditions = {}
    for column_name, filter_value in expanded_conditions:
        if column_name not in column_conditions:
            column_conditions[column_name] = []
        column_conditions[column_name].append(filter_value)
    
    # Apply each column's conditions (OR within column, AND between columns)
    for column_name, values in column_conditions.items():
        if column_name in filtered_df.columns:
            # Create OR mask for all values in this column
            column_mask = pd.Series(False, index=filtered_df.index)
            
            for filter_value in values:
                if isinstance(filter_value, str):
                    # String filtering - try exact match first, then partial match
                    exact_mask = filtered_df[column_name].astype(str) == str(filter_value)
                    if exact_mask.any():
                        mask = exact_mask
                    else:
                        # Fallback to partial match (case-insensitive)
                        mask = filtered_df[column_name].astype(str).str.contains(
                            str(filter_value), case=False, na=False
                        )
                else:
                    # Exact match for non-string values
                    mask = filtered_df[column_name] == filter_value

                column_mask = column_mask | mask
            
            filtered_df = filtered_df[column_mask]
            # Filtering completed silently
        else:
            # Column not found for filtering - skip silently
            pass
    
    return filtered_df

def create_filter_for_multiple_values(column_name: str, values: List[Union[str, int, float]]) -> List[Tuple[str, Union[str, int, float]]]:
    """Create filter tuples for multiple values in the same column.
    
    Args:
        column_name: Name of the column to filter
        values: List of values to include
        
    Returns:
        List of filter tuples that can be used with filter_by parameter
        
    Example:
        # Instead of manually creating:
        filter_by=[('Node', '1'), ('Node', '2'), ('Node', '3')]
        
        # You can use:
        filter_by=create_filter_for_multiple_values('Node', ['1', '2', '3'])
    """
    return [(column_name, value) for value in values]

def sort_dataframe_rows(df: pd.DataFrame, sort_by: Union[str, Tuple[str, str], List[Union[str, Tuple[str, str]]]]) -> pd.DataFrame:
    """Sort DataFrame rows by column(s) with flexible syntax.
    
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
        
    Examples:
        # Simple ascending sort
        sort_by="Node"
        
        # Simple descending sort  
        sort_by=("Load_kN", "desc")
        
        # Multiple columns, all ascending
        sort_by=["Zone", "Node"]
        
        # Multiple columns with mixed directions
        sort_by=[("Zone", "asc"), ("Load_kN", "desc"), "Node"]
    """
    if sort_by is None:
        return df.copy()
    
    sorted_df = df.copy()
    
    # Normalize input to list of tuples
    if isinstance(sort_by, str):
        # Single column name -> ascending
        sort_conditions = [(sort_by, 'asc')]
    elif isinstance(sort_by, tuple):
        # Single tuple -> use as-is
        sort_conditions = [sort_by]
    elif isinstance(sort_by, list):
        # List -> process each element
        sort_conditions = []
        for item in sort_by:
            if isinstance(item, str):
                sort_conditions.append((item, 'asc'))
            elif isinstance(item, tuple):
                sort_conditions.append(item)
            else:
                print(f"⚠️ Warning: Invalid sort condition: {item}")
                continue
    else:
        print(f"⚠️ Warning: Invalid sort_by format: {sort_by}")
        return sorted_df
    
    # Validate and prepare sort parameters
    valid_columns = []
    valid_ascending = []
    
    for column_name, direction in sort_conditions:
        if column_name in sorted_df.columns:
            valid_columns.append(column_name)
            
            # Normalize direction
            direction_lower = str(direction).lower()
            if direction_lower in ['asc', 'ascending', 'up', 'true', '1']:
                valid_ascending.append(True)
            elif direction_lower in ['desc', 'descending', 'down', 'false', '0']:
                valid_ascending.append(False)
            else:
                print(f"⚠️ Warning: Invalid sort direction '{direction}' for column '{column_name}', using 'asc'")
                valid_ascending.append(True)
        else:
            print(f"⚠️ Warning: Column '{column_name}' not found for sorting")
    
    # Apply sorting if we have valid columns
    if valid_columns:
        try:
            # Preserve the original index structure by storing it before sorting
            original_index = sorted_df.index
            
            sorted_df = sorted_df.sort_values(
                by=valid_columns, 
                ascending=valid_ascending,
                na_position='last'  # Put NaN values at the end
            )
            
            # Only reset index if the original was a simple RangeIndex
            # This preserves MultiIndex and other meaningful index structures
            if isinstance(original_index, pd.RangeIndex):
                sorted_df = sorted_df.reset_index(drop=True)
            
            # Create readable sort description
            sort_desc = []
            for col, asc in zip(valid_columns, valid_ascending):
                direction_text = "asc" if asc else "desc"
                sort_desc.append(f"{col} ({direction_text})")
            
            print(f"✓ Sorted by: {', '.join(sort_desc)} ({len(sorted_df)} rows)")
            
        except Exception as e:
            print(f"⚠️ Error during sorting: {e}")
            return df.copy()
    
    return sorted_df

def split_large_table(df: pd.DataFrame, max_rows: Union[int, List[Union[int]]]) -> List[pd.DataFrame]:
    """Split a large DataFrame into smaller chunks for better table display.
    
    Args:
        df: DataFrame to split
        max_rows: Maximum number of rows per table chunk. Can be:
                 - int/float: Fixed size for all chunks
                 - List[int/float]: Custom sizes for each chunk. If there's a remainder after using all values,
                   it creates an additional chunk with the remaining rows.
        
    Returns:
        List of DataFrame chunks
    """
    # Import Union at the top of the function to avoid circular imports
    from typing import Union, List
    
    total_rows = len(df)
    
    # Handle single value (int or float)
    if isinstance(max_rows, (int, float)):
        max_rows = int(max_rows)
        if total_rows <= max_rows:
            return [df]
        
        chunks = []
        for i in range(0, total_rows, max_rows):
            chunk = df.iloc[i:i + max_rows].copy()
            chunks.append(chunk)
        
        return chunks
    
    # Handle list of values
    elif isinstance(max_rows, list):
        if not max_rows:  # Empty list
            return [df]
        
        chunks = []
        start_idx = 0
        
        # Process each specified chunk size
        for chunk_size in max_rows:
            chunk_size = int(chunk_size)
            if start_idx >= total_rows:
                break
            
            end_idx = min(start_idx + chunk_size, total_rows)
            chunk = df.iloc[start_idx:end_idx].copy()
            chunks.append(chunk)
            start_idx = end_idx
        
        # Handle remainder if there are still rows left
        if start_idx < total_rows:
            remainder_chunk = df.iloc[start_idx:].copy()
            chunks.append(remainder_chunk)
        
        return chunks
    
    else:
        raise ValueError(f"max_rows must be int, float, or list of int/float, got {type(max_rows)}")
    
    return chunks

