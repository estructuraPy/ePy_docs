"""DataFrame operations utilities for table creation and data processing.

This module contains specialized DataFrame operations that are commonly used 
in table creation and data processing workflows within the ePy_suite.
"""

from typing import List, Dict, Any, Optional, Tuple, Union
import pandas as pd
import re

# Import the core data processing functions from utils.data
from ePy_docs.files.data import (
    hide_dataframe_columns, process_numeric_columns, convert_dataframe_to_table_with_units,
    safe_parse_numeric, filter_dataframe_rows, sort_dataframe_rows, split_large_table,
    create_filter_for_multiple_values, extract_units_from_columns, is_summary_row,
    clean_first_column_bom
)

# Import decimal configuration functions
from ePy_docs.units.converter import (
    get_decimal_config_from_format_json,
    get_engineering_decimal_config
)


def apply_table_preprocessing(df: pd.DataFrame, 
                             hide_columns: Union[str, List[str]] = None,
                             filter_by: Union[Tuple[str, Union[str, int, float, List]], 
                                           List[Tuple[str, Union[str, int, float, List]]]] = None,
                             sort_by: Union[str, Tuple[str, str], List[Union[str, Tuple[str, str]]]] = None,
                             n_rows: Optional[int] = None) -> pd.DataFrame:
    """Apply comprehensive preprocessing to a DataFrame for table display.
    
    This is a convenience function that applies common preprocessing steps
    in the correct order: filtering -> sorting -> row limiting -> column hiding.
    
    Args:
        df: Input DataFrame
        hide_columns: Column name(s) to hide (string or list of strings)
        filter_by: Filter conditions for rows
        sort_by: Sort conditions for rows
        n_rows: Maximum number of rows to keep
        
    Returns:
        Preprocessed DataFrame ready for table display
    """
    processed_df = df.copy()

    
    # Step 1: Apply row filtering if specified
    if filter_by is not None:
        processed_df = filter_dataframe_rows(processed_df, filter_by)
    
    # Step 2: Apply row sorting if specified
    if sort_by is not None:
        processed_df = sort_dataframe_rows(processed_df, sort_by)
    
    # Step 3: Apply row limit if specified
    if n_rows is not None:
        processed_df = processed_df.head(n_rows)
    
    # Step 4: Reset index if needed and handle MultiIndex columns
    if not isinstance(processed_df.index, pd.RangeIndex):
        # Check if index contains valuable information that should be preserved
        should_preserve_index = False
        if hasattr(processed_df.index, 'names') and processed_df.index.names:
            valuable_index_names = ['node', 'case', 'element', 'foundation', 'support']
            for name in processed_df.index.names:
                if name and any(valuable_name in str(name).lower() for valuable_name in valuable_index_names):
                    should_preserve_index = True
                    break
        
        processed_df = processed_df.reset_index(drop=not should_preserve_index)
    
    # Flatten MultiIndex columns if they exist
    if isinstance(processed_df.columns, pd.MultiIndex):
        processed_df.columns = [' | '.join([str(l) for l in col if l != '' and l is not None]) 
                               for col in processed_df.columns.values]
    
    # Step 5: Prioritize 'Node' column if it exists
    if 'Node' in processed_df.columns and processed_df.columns[0] != 'Node':
        cols = list(processed_df.columns)
        cols.remove('Node')
        processed_df = processed_df[['Node'] + cols]
    
    # Ensure Node column is string type for consistent display
    if 'Node' in processed_df.columns:
        processed_df['Node'] = processed_df['Node'].astype(str)
    
    # Step 6: Apply column hiding if specified (last step)
    if hide_columns is not None:
        processed_df = hide_dataframe_columns(processed_df, hide_columns)
    

    return processed_df


def format_numeric_decimals(df: pd.DataFrame, 
                           decimal_places: Optional[int] = None,
                           exclude_columns: List[str] = None,
                           value_type: str = "general_numeric") -> pd.DataFrame:
    """Format numeric columns to have a specific number of decimal places.
    
    Args:
        df: Input DataFrame
        decimal_places: Number of decimal places to display. If None, loads from JSON config
        exclude_columns: Column names to exclude from formatting
        value_type: Type of values being formatted ('general_numeric', 'conversion_factors', 
                   'forces', 'moments', 'stresses', 'dimensions')
        
    Returns:
        DataFrame with formatted numeric columns
    """
    if exclude_columns is None:
        exclude_columns = ['Node', 'Support', 'Case', 'ID']
    
    # Get decimal places from configuration if not provided
    if decimal_places is None:
        if value_type in ['forces', 'moments', 'stresses', 'dimensions']:
            config = get_engineering_decimal_config(value_type)
            decimal_places = config.get('decimal_places', 2)
        else:
            config = get_decimal_config_from_format_json(value_type)
            decimal_places = config.get('decimal_places', 3)
    
    formatted_df = df.copy()
    
    for col in formatted_df.columns:
        # Skip columns that should not be formatted
        if col in exclude_columns or any(exclude.lower() in col.lower() for exclude in exclude_columns):
            continue
            
        # Check if column is numeric
        if pd.api.types.is_numeric_dtype(formatted_df[col]):
            # Format numeric values to specified decimal places
            formatted_df[col] = formatted_df[col].round(decimal_places)
    
    return formatted_df


def prepare_dataframe_for_display(df: pd.DataFrame, 
                                 apply_unit_conversion: bool = True,
                                 decimal_places: Optional[int] = None,
                                 value_type: str = "general_numeric"
                                 ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Prepare a DataFrame for table display with unit conversion and processing.
    
    Args:
        df: Input DataFrame
        apply_unit_conversion: Whether to apply unit conversion
        decimal_places: Number of decimal places for numeric values. If None, loads from JSON config
        value_type: Type of values being processed ('general_numeric', 'conversion_factors', 
                   'forces', 'moments', 'stresses', 'dimensions')
        
    Returns:
        Tuple of (prepared_df, conversion_log)
    """
    if apply_unit_conversion:
        # Apply unit conversion and processing pipeline
        prepared_df, conversion_log = convert_dataframe_to_table_with_units(df)
    else:
        # Just process numeric columns without unit conversion
        prepared_df = process_numeric_columns(df)
        conversion_log = {"note": "Unit conversion skipped"}
    
    # Apply decimal formatting to numeric columns using configuration
    prepared_df = format_numeric_decimals(prepared_df, decimal_places, value_type=value_type)
    
    return prepared_df, conversion_log


def validate_dataframe_for_table(df: pd.DataFrame, 
                                table_name: str = "table",
                                ) -> bool:
    """Validate that a DataFrame is suitable for table creation.
    
    Args:
        df: DataFrame to validate
        table_name: Name of the table for error messages
        
    Returns:
        True if DataFrame is valid for table creation
        
    Raises:
        ValueError: If DataFrame is not suitable for table creation
    """
    if df is None:
        raise ValueError(f"DataFrame for {table_name} is None")
    
    if df.empty:
        raise ValueError(f"DataFrame for {table_name} is empty")
    
    if len(df.columns) == 0:
        raise ValueError(f"DataFrame for {table_name} has no columns")
    
    
    return True


def analyze_dataframe_structure(df: pd.DataFrame) -> Dict[str, Any]:
    """Analyze DataFrame structure to provide insights for table creation.
    
    Args:
        df: DataFrame to analyze
        
    Returns:
        Dictionary containing analysis results
    """
    analysis = {
        'rows': len(df),
        'columns': len(df.columns),
        'numeric_columns': [],
        'text_columns': [],
        'columns_with_units': {},
        'summary_rows': [],
        'null_percentages': {},
        'unique_value_counts': {}
    }
    
    # Analyze column types and content
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            analysis['numeric_columns'].append(col)
        else:
            analysis['text_columns'].append(col)
        
        # Check for null values
        null_pct = (df[col].isnull().sum() / len(df)) * 100
        analysis['null_percentages'][col] = null_pct
        
        # Count unique values
        analysis['unique_value_counts'][col] = df[col].nunique()
    
    # Extract units from column names
    analysis['columns_with_units'] = extract_units_from_columns(df)
    
    # Check for summary rows
    for idx, row in df.iterrows():
        if is_summary_row(row):
            analysis['summary_rows'].append(idx)
        
        if analysis['columns_with_units']:
            print(f"   🏷️  Units found: {list(analysis['columns_with_units'].values())}")
        
        # Report columns with high null percentages
        high_null_cols = [col for col, pct in analysis['null_percentages'].items() if pct > 50]
        if high_null_cols:
            print(f"   ⚠️  High null percentages: {high_null_cols}")
    
    return analysis
