"""Data processing utilities for ePy_docs.

Refactored module following SOLID principles:
- DataCache: Unified cache management with temporal overrides
- DataProcessor: Core data processing and validation utilities
- DataFrameUtils: DataFrame manipulation and analysis
- TableAnalyzer: Table-specific analysis and dimension calculations

Version: 3.0.0 - Optimized and modularized
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Union, Tuple
import pandas as pd
from pandas.api.types import is_numeric_dtype

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# CACHE MANAGEMENT
# ============================================================================

class DataCache:
    """Unified cache manager for configuration and data files.
    
    Implements caching with temporary override support for testing and
    configuration flexibility.
    """
    
    def __init__(self):
        """Initialize cache with empty state."""
        self._cache: Dict[str, Any] = {}
        self._temp_overrides: Dict[str, Any] = {}
        self._temp_enabled = True
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get cached value with optional temp overrides.
        
        Args:
            key: Cache key
            default: Default value if key not found
            
        Returns:
            Cached value or default
        """
        value = self._cache.get(key, default)
        if self._temp_enabled and key in self._temp_overrides:
            if isinstance(value, dict) and isinstance(self._temp_overrides[key], dict):
                result = value.copy()
                result.update(self._temp_overrides[key])
                return result
            return self._temp_overrides[key]
        return value
    
    def set(self, key: str, value: Any) -> None:
        """Set cached value."""
        self._cache[key] = value
    
    def clear(self, pattern: str = None) -> None:
        """Clear cache entries matching pattern."""
        if pattern is None:
            self._cache.clear()
        else:
            keys_to_remove = [k for k in self._cache.keys() if pattern in k]
            for key in keys_to_remove:
                del self._cache[key]
    
    def set_temp_override(self, key: str, value: Any) -> None:
        """Set temporary override for testing."""
        self._temp_overrides[key] = value
    
    def clear_temp_overrides(self) -> None:
        """Clear all temporary overrides."""
        self._temp_overrides.clear()
    
    def enable_temp(self) -> None:
        """Enable temporary overrides."""
        self._temp_enabled = True
    
    def disable_temp(self) -> None:
        """Disable temporary overrides."""
        self._temp_enabled = False


# Global cache instance
_cache = DataCache()


# ============================================================================
# CACHE UTILITIES
# ============================================================================

def clear_config_cache():
    """Clear all configuration cache."""
    _cache.clear()


def set_temp_config_override(config_type: str, key: str, value: Any) -> None:
    """Set a temporary configuration override for testing."""
    override_key = f"temp_{config_type}_{key}"
    _cache.set_temp_override(override_key, value)


def clear_temp_config_cache(config_type: str = None) -> None:
    """Clear temporary configuration cache."""
    _cache.clear_temp_overrides()


def disable_temp_cache() -> None:
    """Disable temporary cache globally."""
    _cache.disable_temp()


def enable_temp_cache() -> None:
    """Enable temporary cache globally."""
    _cache.enable_temp()


# ============================================================================
# DATA LOADING AND CONFIGURATION
# ============================================================================

class DataProcessor:
    """Core data processing and validation utilities."""
    
    @staticmethod
    def get_reader_config() -> Dict[str, Any]:
        """Load reader configuration using existing config system.
        
        Returns:
            Reader configuration dictionary
        """
        from ePy_docs.core._config import get_config_section
        return get_config_section('reader')
    
    @staticmethod
    def load_cached_files(file_path: str) -> Dict[str, Any]:
        """Load JSON file with optimized caching.
        
        Args:
            file_path: Path to JSON file
            
        Returns:
            Parsed JSON data
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file is invalid
        """
        abs_path = str(Path(file_path).resolve())
        cache_key = f"json_{abs_path}"

        # Check cache first
        cached_data = _cache.get(cache_key)
        if cached_data is not None:
            return cached_data
        
        if not os.path.exists(abs_path):
            raise FileNotFoundError(f"Configuration file not found: {abs_path}")
            
        if not os.path.isfile(abs_path):
            raise ValueError(f"Path is not a file: {abs_path}")
            
        # Read and parse JSON
        with open(abs_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        if not isinstance(data, dict):
            raise ValueError(f"Invalid configuration: {abs_path} does not contain a JSON object")
            
        # Cache the data
        _cache.set(cache_key, data)
        return data
    
    @staticmethod
    def safe_get_nested(data: Dict[str, Any], path: str, default: Any = None) -> Any:
        """Safely get nested value using dot notation.
        
        Args:
            data: Dictionary to search
            path: Dot-separated path (e.g., 'csv_detection.decimal_separator')
            default: Default value if path not found
            
        Returns:
            Value at path or default
        """
        if not isinstance(data, dict) or not path:
            return default
            
        try:
            result = data
            for key in path.split('.'):
                result = result.get(key, default) if isinstance(result, dict) else default
            return result
        except (AttributeError, TypeError):
            return default

    @staticmethod
    def safe_parse_numeric(value: Any) -> float:
        """Parse value to float using reader configuration.
        
        Args:
            value: Value to parse
            
        Returns:
            Parsed float value
            
        Raises:
            ValueError: If value cannot be parsed as numeric
        """
        if value is None or pd.isna(value):
            raise ValueError("Cannot parse None or NaN value")

        # Handle numeric types
        if isinstance(value, (int, float)):
            if pd.isna(value):
                raise ValueError("Cannot parse NaN value")
            return float(value)

        # Get configuration
        config = DataProcessor.get_reader_config()
        
        # Convert to string and clean
        str_value = str(value).strip().lower()
        
        # Check non-numeric patterns
        non_numeric_patterns = DataProcessor.safe_get_nested(
            config, 'csv_detection.non_numeric_patterns', 
            ['nan', 'n/a', 'none', 'null', 'unknown', 'totals']
        )
        
        if any(str_value == pattern.lower() for pattern in non_numeric_patterns):
            raise ValueError(f"Non-numeric pattern detected: {value}")

        # Handle empty strings and dashes
        if not str_value or str_value == '-':
            raise ValueError(f"Empty or dash value: {value}")

        # Get separators from config
        decimal_sep = DataProcessor.safe_get_nested(config, 'csv_detection.decimal_separator', '.')
        thousand_sep = DataProcessor.safe_get_nested(config, 'csv_detection.thousand_separator', '')
        
        try:
            # Clean the string
            clean_str = str_value
            if thousand_sep:
                clean_str = clean_str.replace(thousand_sep, '')
            if decimal_sep != '.':
                clean_str = clean_str.replace(decimal_sep, '.')
            return float(clean_str)
            
        except ValueError as e:
            raise ValueError(f"Cannot parse numeric value: {value}") from e


# ============================================================================
# DATAFRAME UTILITIES
# ============================================================================

class DataFrameUtils:
    """DataFrame manipulation and analysis utilities."""
    
    @staticmethod
    def hide_columns(df: pd.DataFrame, 
                    hide_columns: Optional[Union[str, List[str]]] = None) -> pd.DataFrame:
        """Hide columns from DataFrame based on exact or partial name matching.
        
        Args:
            df: Input DataFrame
            hide_columns: Column names or patterns to hide
            
        Returns:
            DataFrame with specified columns hidden
            
        Raises:
            TypeError: If df is not a DataFrame
        """
        if not isinstance(df, pd.DataFrame):
            raise TypeError(f"Expected pandas DataFrame, got {type(df).__name__}")
        
        if not hide_columns:
            return df.copy()
        
        # Normalize to list
        columns_to_hide = [hide_columns] if isinstance(hide_columns, str) else list(hide_columns)
        
        # Find columns to hide using comprehension
        hidden_columns = {
            col for pattern in columns_to_hide 
            for col in df.columns 
            if isinstance(pattern, str) and (pattern == col or pattern.lower() in col.lower())
        }
        
        # Return DataFrame without hidden columns
        visible_columns = [col for col in df.columns if col not in hidden_columns]
        return df[visible_columns].copy()

    @staticmethod
    def process_numeric_columns(df: pd.DataFrame, 
                              id_columns: Optional[List[str]] = None) -> pd.DataFrame:
        """Process DataFrame columns to convert numeric data to appropriate types.
        
        Args:
            df: Input DataFrame
            id_columns: Columns to skip processing
            
        Returns:
            DataFrame with numeric columns properly typed
            
        Raises:
            TypeError: If df is not a DataFrame
        """
        if not isinstance(df, pd.DataFrame):
            raise TypeError(f"Expected pandas DataFrame, got {type(df).__name__}")
        
        id_columns = set(id_columns or [])
        processed_df = df.copy()
        
        # Get configuration
        config = DataProcessor.get_reader_config()
        sample_size = DataProcessor.safe_get_nested(config, 'csv_detection.sample_rows', 10)
        threshold = DataProcessor.safe_get_nested(config, 'csv_detection.numeric_threshold', 0.5)
        
        for col in processed_df.columns:
            if col in id_columns or is_numeric_dtype(processed_df[col]):
                continue
                
            # Only process object columns with non-null values
            non_null = processed_df[col].dropna()
            if non_null.empty or processed_df[col].dtype != 'object':
                continue
                
            # Check if majority of sample is numeric
            sample = non_null.head(sample_size)
            numeric_count = sum(1 for val in sample if DataFrameUtils._is_numeric_value(val))
            
            if numeric_count / len(sample) >= threshold:
                try:
                    processed_df[col] = pd.to_numeric(processed_df[col])
                except (ValueError, TypeError):
                    pass  # Keep original type if conversion fails
        
        return processed_df
    
    @staticmethod
    def _is_numeric_value(val) -> bool:
        """Check if value can be parsed as numeric."""
        try:
            DataProcessor.safe_parse_numeric(val)
            return True
        except ValueError:
            return False

    @staticmethod
    def sort_rows(df: pd.DataFrame, 
                 sort_by: Union[str, Tuple[str, str], List[Union[str, Tuple[str, str]]]]) -> pd.DataFrame:
        """Sort DataFrame rows by column(s) with flexible syntax.
        
        Args:
            df: DataFrame to sort
            sort_by: Sort specification (column name, tuple, or list)
            
        Returns:
            Sorted DataFrame
        """
        if sort_by is None:
            return df.copy()
        
        # Normalize to list of tuples
        sort_conditions = DataFrameUtils._normalize_sort_conditions(sort_by)
        
        # Validate and extract columns and directions
        columns, ascending = DataFrameUtils._validate_sort_conditions(df, sort_conditions)
        
        # Apply sorting
        sorted_df = df.sort_values(by=columns, ascending=ascending, na_position='last')
        
        # Reset index for RangeIndex
        if isinstance(df.index, pd.RangeIndex):
            sorted_df = sorted_df.reset_index(drop=True)
        
        return sorted_df

    @staticmethod
    def _normalize_sort_conditions(sort_by) -> List[Tuple[str, str]]:
        """Normalize sort_by input to list of tuples."""
        if isinstance(sort_by, str):
            return [(sort_by, 'desc')]  # Default to descending
        elif isinstance(sort_by, tuple):
            return [sort_by]
        elif isinstance(sort_by, list):
            conditions = []
            for item in sort_by:
                if isinstance(item, str):
                    conditions.append((item, 'desc'))  # Default to descending
                elif isinstance(item, tuple):
                    conditions.append(item)
                else:
                    raise ValueError(f"Invalid sort condition: {item}")
            return conditions
        else:
            raise ValueError(f"Invalid sort_by format: {type(sort_by)}")

    @staticmethod
    def _validate_sort_conditions(df: pd.DataFrame, sort_conditions: List[Tuple[str, str]]) -> Tuple[List[str], List[bool]]:
        """Validate sort conditions and return columns and ascending flags."""
        columns = []
        ascending = []
        
        for column_name, direction in sort_conditions:
            if column_name not in df.columns:
                raise ValueError(f"Column '{column_name}' not found in DataFrame")
            
            columns.append(column_name)
            
            # Parse direction
            direction_lower = str(direction).lower()
            if direction_lower in ['asc', 'ascending', 'up', 'true', '1']:
                ascending.append(True)
            elif direction_lower in ['desc', 'descending', 'down', 'false', '0']:
                ascending.append(False)
            else:
                raise ValueError(f"Invalid sort direction '{direction}' for column '{column_name}'")
        
        return columns, ascending

    @staticmethod
    def split_large_table(df: pd.DataFrame, max_rows: Union[int, List[int]]) -> List[pd.DataFrame]:
        """Split DataFrame into chunks based on row limits.
        
        Args:
            df: DataFrame to split
            max_rows: Maximum rows per chunk (int) or custom chunk sizes (list)
            
        Returns:
            List of DataFrame chunks
            
        Raises:
            ValueError: If max_rows format is invalid
        """
        total_rows = len(df)
        
        if isinstance(max_rows, (int, float)):
            # Uniform chunks
            chunk_size = int(max_rows)
            if total_rows <= chunk_size:
                return [df]
            return [df.iloc[i:i + chunk_size].copy() for i in range(0, total_rows, chunk_size)]
        
        elif isinstance(max_rows, list):
            if not max_rows:
                return [df]
            
            # Custom chunks
            chunk_sizes = [int(size) for size in max_rows]
            chunks = []
            start_idx = 0
            
            for chunk_size in chunk_sizes:
                end_idx = min(start_idx + chunk_size, total_rows)
                if start_idx >= total_rows:
                    break
                chunks.append(df.iloc[start_idx:end_idx].copy())
                start_idx = end_idx
            
            # Handle remainder
            if start_idx < total_rows:
                chunks.append(df.iloc[start_idx:].copy())
            
            return chunks
        
        else:
            raise ValueError(f"max_rows must be int, float, or list of int/float, got {type(max_rows)}")


# ============================================================================
# TABLE ANALYSIS
# ============================================================================

class TableAnalyzer:
    """Table-specific analysis and dimension calculations."""
    
    # Configuration constants from external config
    _WIDTH_FACTORS = {
        (0, 3): 0.7,
        (3, 8): 0.9,
        (8, 15): 1.0,
        (15, 25): 1.2,
        (25, 35): 1.4,
        (35, float('inf')): 1.6
    }
    _SPECIAL_CHAR_FACTOR = 1.05
    _SPECIAL_CHARS = ['²', '³', '⁰', '¹', '⁴', '⁵', '⁶', '⁷', '⁸', '⁹', '·', '×', '÷', '±', '≤', '≥']
    
    @staticmethod
    def calculate_column_width(col_index: int, column_name: str, df: pd.DataFrame) -> float:
        """Calculate specific width factor for each column.
        
        Args:
            col_index: Column index in DataFrame
            column_name: Name of the column
            df: DataFrame containing the data
            
        Returns:
            Width factor for the column
        """
        max_content_length = len(str(column_name))
        has_special_chars = False
        
        # Find maximum content length
        for row_idx in range(len(df)):
            cell_value = df.iloc[row_idx, col_index]
            cell_str = str(cell_value)
            
            # Check for special characters
            if not has_special_chars and any(char in cell_str for char in TableAnalyzer._SPECIAL_CHARS):
                has_special_chars = True
            
            # Handle multiline content
            if '\n' in cell_str:
                lines = cell_str.split('\n')
                max_line_length = max(len(line) for line in lines)
                max_content_length = max(max_content_length, max_line_length)
            else:
                max_content_length = max(max_content_length, len(cell_str))
        
        # Determine width factor based on content length
        width_factor = 1.0  # default
        for (min_len, max_len), factor in TableAnalyzer._WIDTH_FACTORS.items():
            if min_len <= max_content_length < max_len:
                width_factor = factor
                break
        
        # Apply special character factor
        if has_special_chars:
            width_factor *= TableAnalyzer._SPECIAL_CHAR_FACTOR
        
        return width_factor

    @staticmethod
    def calculate_row_height(row_index: int, df: pd.DataFrame, is_header: bool,
                           font_size_header: float, font_size_content: float,
                           layout_style: str, font_family: str) -> float:
        """Calculate necessary row height dynamically.
        
        Args:
            row_index: Row index in DataFrame
            df: DataFrame containing the data
            is_header: Whether this is a header row
            font_size_header: Font size for headers
            font_size_content: Font size for content
            layout_style: Layout style name
            font_family: Font family name
            
        Returns:
            Height factor relative to default cell height
        """
        # Determine base font size for this row
        base_font_size = float(font_size_header if is_header else font_size_content)
        
        # Count maximum lines in this row
        max_lines_in_row = TableAnalyzer._count_max_lines(df, row_index, is_header)
        
        # Calculate line height (baseline: 1.3x font size for readability)
        line_height = base_font_size * 1.3
        
        # Font type adjustment
        font_type_factor = 1.15 if layout_style == 'minimal' or font_family == 'handwritten' else 1.0
        
        # Calculate cell padding proportional to font size
        padding_per_cell = base_font_size * (0.25 if is_header else 0.05)
        
        # Total content height needed
        content_height = line_height * max_lines_in_row * font_type_factor
        total_height = content_height + padding_per_cell
        
        # Headers need additional spacing
        if is_header:
            total_height *= 1.30
        
        # Convert to height factor relative to matplotlib's default
        default_cell_height = base_font_size * 1.2
        height_factor = max(total_height / default_cell_height, 1.4 if is_header else 1.2)
        
        return height_factor
    
    @staticmethod
    def _count_max_lines(df: pd.DataFrame, row_index: int, is_header: bool) -> int:
        """Count maximum lines in a row."""
        max_lines = 1
        
        if is_header:
            for col in df.columns:
                col_str = str(col)
                line_count = col_str.count('\n') + 1
                max_lines = max(max_lines, line_count)
                
                # Auto-wrap estimation for long headers
                if len(col_str) > 20:
                    estimated_lines = len(col_str) // 20 + 1
                    max_lines = max(max_lines, estimated_lines)
        else:
            if row_index < len(df):
                for col in df.columns:
                    cell_value = df.iloc[row_index, df.columns.get_loc(col)]
                    cell_str = str(cell_value)
                    
                    line_count = cell_str.count('\n') + 1
                    max_lines = max(max_lines, line_count)
                    
                    # Auto-wrap estimation for long content
                    if len(cell_str) > 25:
                        estimated_lines = len(cell_str) // 25 + 1
                        max_lines = max(max_lines, estimated_lines)
        
        return max_lines

    @staticmethod
    def detect_category(df: pd.DataFrame, config: Dict) -> Tuple[str, Optional[List[str]]]:
        """Detect table category and suggest highlight columns.
        
        Args:
            df: DataFrame to analyze
            config: Tables configuration with category rules
            
        Returns:
            Tuple of (category_name, highlight_columns)
        """
        category_rules = config.get('category_rules', {})
        
        if not category_rules:
            return 'general', None
        
        column_names = [str(col).lower() for col in df.columns]
        
        max_matches = 0
        detected_category = 'general'
        suggested_columns = None
        
        for category, rules in category_rules.items():
            keywords = rules.get('keywords', [])
            highlight_cols = rules.get('highlight_columns', [])
            
            matches = sum(1 for keyword in keywords 
                         if any(keyword in col_name for col_name in column_names))
            
            if matches > max_matches:
                max_matches = matches
                detected_category = category
                
                actual_highlight_columns = [
                    original_col for highlight_pattern in highlight_cols
                    for original_col in df.columns
                    if highlight_pattern.lower() in str(original_col).lower()
                ]
                
                suggested_columns = actual_highlight_columns if actual_highlight_columns else None
        
        return detected_category, suggested_columns


# ============================================================================
# TABLE PREPARATION AND DATA TRANSFORMATION
# ============================================================================

class TablePreparation:
    """Prepare and transform DataFrames for table rendering.
    
    This class centralizes all data preparation operations that should occur
    before table rendering, reducing complexity in _tables.py and following
    the Single Responsibility Principle.
    """
    
    @staticmethod
    def prepare_table_data(df: pd.DataFrame,
                          hide_columns: Optional[Union[str, List[str]]] = None,
                          filter_by: Optional[Dict[str, Any]] = None,
                          sort_by: Optional[Union[str, List[str]]] = None) -> pd.DataFrame:
        """Prepare DataFrame for rendering by applying transformations.
        
        This is the main entry point for table data preparation. It applies
        transformations in the correct order: filter → sort → hide columns.
        
        Args:
            df: Input DataFrame
            hide_columns: Column names or patterns to hide
            filter_by: Dictionary to filter rows {column: value or [values]}
            sort_by: Column name(s) to sort by
            
        Returns:
            Prepared DataFrame ready for rendering
            
        Example:
            prepared_df = TablePreparation.prepare_table_data(
                df,
                hide_columns=['ID', 'Internal'],
                filter_by={'Status': 'Active', 'Type': ['A', 'B']},
                sort_by='Date'
            )
        """
        result = df.copy()
        
        # Step 1: Filter rows (reduces data before sorting)
        if filter_by:
            result = TablePreparation._filter_rows(result, filter_by)
        
        # Step 2: Sort rows (after filtering, before column hiding)
        if sort_by:
            result = DataFrameUtils.sort_rows(result, sort_by)
        
        # Step 3: Hide columns (last step, only affects display)
        if hide_columns:
            result = DataFrameUtils.hide_columns(result, hide_columns)
        
        return result
    
    @staticmethod
    def _filter_rows(df: pd.DataFrame, filter_by: Dict[str, Any]) -> pd.DataFrame:
        """Filter DataFrame rows based on column values.
        
        Args:
            df: Input DataFrame
            filter_by: Dictionary mapping column names to filter values
                      - Single value: {'Status': 'Active'}
                      - Multiple values: {'Type': ['A', 'B', 'C']}
                      
        Returns:
            Filtered DataFrame
            
        Raises:
            ValueError: If filter column not found in DataFrame
        """
        if not filter_by:
            return df.copy()
        
        result = df.copy()
        
        for column, value in filter_by.items():
            # Validate column exists
            if column not in result.columns:
                raise ValueError(f"Filter column '{column}' not found in DataFrame. "
                               f"Available columns: {list(result.columns)}")
            
            # Apply filter based on value type
            if isinstance(value, list):
                # Multiple values - use .isin()
                result = result[result[column].isin(value)]
            else:
                # Single value - direct comparison
                result = result[result[column] == value]
        
        return result
    
    @staticmethod
    def split_for_rendering(df: pd.DataFrame,
                           max_rows_per_table: Union[int, List[int]]) -> List[pd.DataFrame]:
        """Split DataFrame into chunks for multi-page rendering.
        
        This is a convenience wrapper around DataFrameUtils.split_large_table()
        specifically for table rendering context.
        
        Args:
            df: DataFrame to split
            max_rows_per_table: Maximum rows per chunk (int) or custom sizes (list)
            
        Returns:
            List of DataFrame chunks ready for rendering
            
        Example:
            # Fixed size chunks
            chunks = TablePreparation.split_for_rendering(df, max_rows_per_table=20)
            
            # Variable size chunks
            chunks = TablePreparation.split_for_rendering(df, max_rows_per_table=[10, 15, 20])
        """
        return DataFrameUtils.split_large_table(df, max_rows_per_table)


# ============================================================================
# TABLE WIDTH AND DIMENSION CALCULATIONS
# ============================================================================

class TableDimensionCalculator:
    """Calculate table dimensions and widths for rendering.
    
    Handles width calculations for multi-column layouts and dimension
    analysis for optimal table rendering.
    """
    
    @staticmethod
    def calculate_width_string(column_span: Optional[int], 
                               document_columns: int) -> str:
        """Calculate LaTeX width string for table based on column span.
        
        Args:
            column_span: Number of columns to span (None = 1)
            document_columns: Total columns in document layout
            
        Returns:
            Width string like "\\columnwidth", "\\linewidth", or "\\textwidth"
            
        Note:
            In multicol environments:
            - column_span = 1: Uses \\columnwidth (width of one column)
            - column_span >= 2: Uses \\textwidth (full page width, requires figure*/table*)
        """
        if column_span is None:
            column_span = 1
        
        # Limit column_span to document_columns (prevent user errors)
        if column_span > document_columns:
            column_span = document_columns
        
        # Single column layout
        if document_columns == 1:
            return "1.0\\linewidth"
        
        # Multi-column layout (e.g., twocolumn, multicol)
        if column_span >= 2:
            # Spanning multiple columns requires figure*/table* environment
            # Use full text width (1.0\textwidth ensures no extra margins)
            return "1.0\\textwidth"
        else:
            # Single column within multicol environment
            return "\\columnwidth"
    
    @staticmethod
    def calculate_table_height(df: pd.DataFrame, 
                              row_height: float = 0.3) -> float:
        """Calculate optimal table height based on content.
        
        Args:
            df: DataFrame to analyze
            row_height: Base row height in inches
            
        Returns:
            Calculated height in inches (clamped 2-12 inches)
        """
        num_rows = len(df) + 1  # Include header
        
        # Check for content that will likely be wrapped
        wrapped_rows = sum(
            1 for _, row in df.iterrows()
            if any(len(str(val)) > 12 for val in row if pd.notna(val))
        )
        
        # Check if headers will be wrapped
        header_wrapped = any(len(str(col)) > 10 for col in df.columns)
        
        # Calculate height with wrapping adjustments
        header_height = row_height * 1.4 if header_wrapped else row_height
        regular_rows = num_rows - 1 - wrapped_rows
        wrapped_row_height = row_height * 1.3
        
        calculated_height = (
            header_height + 
            (regular_rows * row_height) + 
            (wrapped_rows * wrapped_row_height) + 
            0.5  # Padding
        )
        
        return min(max(calculated_height, 2.0), 12.0)
    
    @staticmethod
    def get_column_class(column_span: Optional[int], 
                        document_columns: int) -> str:
        """Get Quarto CSS column class for layout.
        
        Args:
            column_span: Number of columns to span
            document_columns: Total columns in document
            
        Returns:
            Quarto column class name
            
        Note:
            In multicol environments, elements with column_span >= 2 are rendered
            using figure*/table* LaTeX environments, so the column class is less
            relevant (but kept as column-page for consistency).
        """
        if column_span is None or column_span == 1:
            return "column-body"
        else:
            # column_span >= 2: spans multiple columns (uses figure*/table* in LaTeX)
            return "column-page"


# ============================================================================
# TABLE ANALYSIS
# ============================================================================

class TableContentAnalyzer:
    """Analyze table content for optimal styling and rendering."""
    
    @staticmethod
    def needs_wrapping(df: pd.DataFrame, max_cell_length: int = 12) -> bool:
        """Check if table content needs text wrapping.
        
        Args:
            df: DataFrame to analyze
            max_cell_length: Maximum cell length before wrapping
            
        Returns:
            True if wrapping is needed
        """
        # Check data cells
        for _, row in df.iterrows():
            if any(len(str(val)) > max_cell_length for val in row if pd.notna(val)):
                return True
        
        # Check headers
        if any(len(str(col)) > max_cell_length for col in df.columns):
            return True
        
        return False
    
    @staticmethod
    def calculate_column_widths(df: pd.DataFrame, 
                               total_width: float) -> List[float]:
        """Calculate proportional column widths based on content.
        
        Args:
            df: DataFrame to analyze
            total_width: Total available width in inches
            
        Returns:
            List of column widths in inches
        """
        # Calculate content-based weights
        col_weights = []
        for col in df.columns:
            # Consider header length and max content length
            header_len = len(str(col))
            max_content = max(
                (len(str(val)) for val in df[col] if pd.notna(val)), 
                default=0
            )
            col_weights.append(max(header_len, max_content))
        
        # Normalize to total width
        total_weight = sum(col_weights)
        if total_weight == 0:
            # Equal distribution if no content
            return [total_width / len(df.columns)] * len(df.columns)
        
        return [total_width * (w / total_weight) for w in col_weights]
    
    @staticmethod
    def calculate_optimal_width(df: pd.DataFrame, 
                               base_width: float,
                               style_config: Optional[Dict] = None) -> float:
        """Calculate optimal table width based on content and configuration.
        
        Args:
            df: DataFrame to analyze
            base_width: Base width from configuration
            style_config: Optional style configuration dict
            
        Returns:
            Calculated width in inches (clamped 4-14 inches)
            
        Raises:
            ValueError: If base_width not provided
        """
        if base_width is None or base_width <= 0:
            raise ValueError("base_width must be a positive number")
        
        num_cols = len(df.columns)
        
        # Check if we have long headers or content that might need wrapping
        max_header_length = max(len(str(col)) for col in df.columns) if len(df.columns) > 0 else 0
        max_content_length = 0
        for col in df.columns:
            # Get non-null values for this column
            non_null_values = [str(val) for val in df[col] if pd.notna(val)]
            col_max = max(len(val) for val in non_null_values) if non_null_values else 0
            max_content_length = max(max_content_length, col_max)
        
        # Adjust width based on content complexity
        width_multiplier = 1.0
        if max_header_length > 15 or max_content_length > 20:
            width_multiplier = 1.2  # Wider for long content
        elif max_header_length > 10 or max_content_length > 15:
            width_multiplier = 1.1  # Slightly wider
        
        # Adjust for number of columns
        if num_cols > 5:
            return min(base_width * width_multiplier * 1.1, 14.0)
        elif num_cols < 3:
            return max(base_width * width_multiplier * 0.9, 4.0)
        
        return base_width * width_multiplier
    
    @staticmethod
    def calculate_optimal_height(df: pd.DataFrame,
                                base_row_height: float = 0.3) -> float:
        """Calculate optimal table height based on content and wrapping.
        
        Args:
            df: DataFrame to analyze
            base_row_height: Base row height in inches
            
        Returns:
            Calculated height in inches (clamped 2-12 inches)
        """
        num_rows = len(df) + 1  # Include header
        
        # Check for content that will likely be wrapped
        wrapped_rows = 0
        for idx, row in df.iterrows():
            row_needs_wrapping = any(len(str(val)) > 12 for val in row if pd.notna(val))
            if row_needs_wrapping:
                wrapped_rows += 1
        
        # Check if headers will be wrapped
        header_wrapped = any(len(str(col)) > 10 for col in df.columns)
        
        # Adjust height based on wrapping
        if header_wrapped:
            header_height = base_row_height * 1.4  # Extra space for wrapped headers
        else:
            header_height = base_row_height
            
        if wrapped_rows > 0:
            # Some rows have wrapped content
            regular_rows = num_rows - 1 - wrapped_rows
            wrapped_row_height = base_row_height * 1.3
            calculated_height = header_height + (regular_rows * base_row_height) + (wrapped_rows * wrapped_row_height)
        else:
            # No wrapped content
            calculated_height = header_height + ((num_rows - 1) * base_row_height)
        
        # Add some padding
        calculated_height += 0.5
        
        return min(max(calculated_height, 2.0), 12.0)  # Clamp between 2 and 12 inches
    
    @staticmethod
    def calculate_width_from_columns(columns: Union[float, List[float], None], 
                                     document_type: str) -> Optional[float]:
        """Calculate width in inches from columns specification.
        
        Args:
            columns: Column specification (float or list)
            document_type: Document type for configuration lookup
            
        Returns:
            Calculated width in inches or None
            
        Raises:
            ValueError: If calculation fails or configuration missing
        """
        if columns is None:
            return None
        
        if isinstance(columns, list):
            return columns[0] if columns else None
        
        # Use ColumnWidthCalculator for width calculation
        try:
            from ePy_docs.core._document import ColumnWidthCalculator
            calculator = ColumnWidthCalculator()
            
            if columns == 1:
                layout_columns = 1  # Full width
            else:
                # Get layout columns from config
                try:
                    from ePy_docs.core._config import ModularConfigLoader
                    config_loader = ModularConfigLoader()
                    doc_config = config_loader.load_external('document_types')
                    
                    doc_types = doc_config.get('document_types', {})
                    if document_type not in doc_types:
                        raise ValueError(f"Document type '{document_type}' not found in configuration")
                    
                    type_config = doc_types[document_type]
                    if 'default_columns' not in type_config:
                        raise ValueError(f"Missing 'default_columns' for document type '{document_type}'")
                    
                    layout_columns = type_config['default_columns']
                except Exception as e:
                    raise ValueError(f"Failed to load layout columns for '{document_type}': {e}")
            
            return calculator.calculate_width(document_type, layout_columns, columns)
            
        except Exception as e:
            # Configuration required - no hardcoded fallbacks
            raise ValueError(f"Width calculation failed for document_type '{document_type}': {e}. "
                           "Ensure ColumnWidthCalculator is properly configured.")
    
    @staticmethod
    def calculate_cell_lines(text_value, is_header: bool, max_width: int = 12,
                            wrap_text_func=None) -> int:
        """Calculate number of lines needed for cell content.
        
        Args:
            text_value: Cell content to measure
            is_header: Whether this is a header cell
            max_width: Maximum character width before wrapping
            wrap_text_func: Optional text wrapping function
            
        Returns:
            Number of lines needed for content
        """
        text_str = str(text_value) if text_value is not None else ""
        wrap_width = 10 if is_header else max_width
        
        if len(text_str) <= wrap_width:
            return 1
        
        if wrap_text_func is not None:
            wrapped_text = wrap_text_func(text_str, wrap_width)
            return len(wrapped_text.split('\n')) if isinstance(wrapped_text, str) else 1
        
        # Simple wrapping if no function provided
        import textwrap
        wrapped_lines = textwrap.wrap(text_str, width=wrap_width)
        return len(wrapped_lines) if wrapped_lines else 1


