"""Data processing utilities for ePy_docs.

Provides functions for data loading, caching, and transformation to support
various file formats and unit conversion operations.
"""

import os
import re
import json
from functools import lru_cache
from typing import Dict, Any, List, Optional, Union, Tuple
import pandas as pd
from pandas.api.types import is_numeric_dtype

# Global cache for JSON data to avoid redundant file operations
_JSON_DATA_CACHE = {}

@lru_cache(maxsize=32)
def _load_cached_json(file_path: str) -> Dict[str, Any]:
    """Load JSON file with caching and strict error handling.
    
    Args:
        file_path: Path to the JSON file.
        
    Returns:
        Dictionary containing loaded JSON data.
        
    Raises:
        FileNotFoundError: If file does not exist
        ValueError: If file is empty or contains invalid JSON
        RuntimeError: If file cannot be read
        
    Assumptions:
        File system access is available for reading operations.
        JSON files follow standard format specifications.
    """
    global _JSON_DATA_CACHE
    
    if file_path in _JSON_DATA_CACHE:
        return _JSON_DATA_CACHE[file_path]
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"JSON file not found: {file_path}")
    
    if os.path.getsize(file_path) == 0:
        raise ValueError(f"JSON file is empty: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        if data is None:
            raise ValueError(f"JSON file contains null data: {file_path}")
            
        _JSON_DATA_CACHE[file_path] = data
        return data
        
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in file {file_path}: {e}")
    except Exception as e:
        raise RuntimeError(f"Error reading JSON file {file_path}: {e}")


def _safe_get_nested(data: Dict[str, Any], path: str, default: Any = None) -> Any:
    """Get a nested value from a dictionary using dot notation.
    
    Args:
        data: Dictionary to access.
        path: Dot-separated path to nested value.
        default: Value to return if path not found.
        
    Returns:
        Value at the specified path or default if path not found.
    """
    if not path:
        return default
        
    keys = path.split('.')
    result = data
    
    try:
        for key in keys:
            result = result[key]
        return result
    except (KeyError, TypeError):
        return default


def safe_parse_numeric(value: Any) -> float:
    """Parse a value to float, handling various formats."""
    if value is None or pd.isna(value):
        raise ValueError(f"Cannot parse None or NaN value: {value}")

    if isinstance(value, (int, float)):
        if pd.isna(value):
            raise ValueError(f"Cannot parse NaN value: {value}")
        return float(value)

    if not isinstance(value, str):
        return float(value)

    clean_str = str(value).strip()
    non_numeric_keywords = [
        'nan', 'n/a', 'none', 'null', 'cus', 'sum',
        'precision', 'check val', 'unknown', 'totals', 'inf', '-inf'
    ]

    if any(clean_str.lower().startswith(keyword) for keyword in non_numeric_keywords):
        raise ValueError(f"Cannot parse non-numeric value: {clean_str}")

    if clean_str in ('', '-'):
        raise ValueError(f"Cannot parse non-numeric value: {clean_str}")

    try:
        return float(clean_str)
    except ValueError:
        try:
            if ',' in clean_str and '.' not in clean_str:
                return float(clean_str.replace(',', '.'))
            if '.' in clean_str and ',' in clean_str:
                no_thousands = re.sub(r'(?<=\d)\.(?=\d{3}(?:\D|$))', '', clean_str)
                return float(no_thousands.replace(',', '.'))
            return float(clean_str.replace(',', '.'))
        except Exception as e:
            raise ValueError(f"Cannot parse numeric value: {clean_str} - Error: {e}")


def hide_dataframe_columns(df: pd.DataFrame, hide_columns: Union[str, List[str]]) -> pd.DataFrame:
    """Hide columns from a DataFrame by exact or partial name matching.
    
    Args:
        df: DataFrame to process
        hide_columns: Column name(s) to hide (string or list of strings)
        
    Returns:
        DataFrame with specified columns hidden
    """
    if hide_columns is None:
        return df.copy()
    
    # Convert single string to list
    if isinstance(hide_columns, str):
        hide_columns = [hide_columns]
    
    # Get columns to keep (inverse of hide)
    columns_to_keep = []
    columns_to_hide = []
    
    for col in df.columns:
        should_hide = False
        for hide_pattern in hide_columns:
            # Exact match first
            if col == hide_pattern:
                should_hide = True
                break
            # Partial match (case-insensitive)
            elif hide_pattern.lower() in col.lower():
                should_hide = True
                break
        
        if should_hide:
            columns_to_hide.append(col)
        else:
            columns_to_keep.append(col)
    
    if columns_to_hide:
        pass  # Columns hidden silently
    
    return df[columns_to_keep].copy()


def process_numeric_columns(df: pd.DataFrame, id_columns: Optional[List[str]] = None) -> pd.DataFrame:
    """Process numeric columns in a DataFrame, handling various formats and edge cases.
    
    Args:
        df: DataFrame to process
        id_columns: List of column names to treat as identifiers (not numeric)
        
    Returns:
        DataFrame with processed numeric columns
    """
    if id_columns is None:
        id_columns = []
    
    processed_df = df.copy()
    
    for col in processed_df.columns:
        if col in id_columns:
            continue
            
        # Try to convert to numeric if it's not already
        if not is_numeric_dtype(processed_df[col]):
            try:
                # Handle common text patterns that should remain as text
                if processed_df[col].dtype == 'object':
                    # Check if column contains mostly non-numeric data
                    sample_values = processed_df[col].dropna().head(10)
                    numeric_count = 0
                    
                    for val in sample_values:
                        try:
                            safe_parse_numeric(val)
                            numeric_count += 1
                        except:
                            pass
                    
                    # If less than half are numeric, keep as object
                    if numeric_count < len(sample_values) / 2:
                        continue
                
                # Attempt conversion for potentially numeric columns
                try:
                    processed_df[col] = pd.to_numeric(processed_df[col])
                except (ValueError, TypeError):
                    # Keep original dtype if conversion fails
                    pass
                    
            except Exception:
                # Keep original dtype if any other error occurs during processing
                continue
    
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

