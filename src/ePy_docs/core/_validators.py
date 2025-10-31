"""
Input Validation Module

CONSTITUTIONAL PRINCIPLE: SECURITY LAYER
All validation logic centralized here. API layer only imports and calls.

Provides:
- Type validation (DataFrame, str, list, Path)
- Value validation (non-empty, format checks)
- Business rule validation (file exists, valid extensions)
"""

import re
from pathlib import Path
from typing import Any
import pandas as pd


def validate_dataframe(df: Any, param_name: str = "df") -> None:
    """
    Validate that a parameter is a non-empty pandas DataFrame.
    
    Args:
        df: The value to validate as a DataFrame
        param_name: Name of the parameter for error messages (default: "df")
        
    Raises:
        TypeError: If df is None or not a pandas DataFrame
        ValueError: If df is an empty DataFrame
        
    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({"A": [1, 2, 3]})
        >>> validate_dataframe(df)  # No error
        >>> validate_dataframe(None)  # TypeError
        >>> validate_dataframe(pd.DataFrame())  # ValueError
    """
    if df is None:
        raise TypeError(f"Parameter '{param_name}' must be a DataFrame, not None")
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"Parameter '{param_name}' must be a DataFrame, got {type(df).__name__}")
    if df.empty:
        raise ValueError(f"Parameter '{param_name}' cannot be an empty DataFrame")


def validate_string(value: Any, param_name: str, allow_empty: bool = False, allow_none: bool = False) -> None:
    """
    Validate that a parameter is a non-empty string.
    
    Args:
        value: The value to validate as a string
        param_name: Name of the parameter for error messages
        allow_empty: If True, allows empty strings (default: False)
        allow_none: If True, allows None values (default: False)
        
    Raises:
        TypeError: If value is not a string (and not None when allow_none=True)
        ValueError: If value is empty or whitespace-only (when allow_empty=False)
        
    Example:
        >>> validate_string("Hello", "text")  # No error
        >>> validate_string("", "text")  # ValueError
        >>> validate_string("", "text", allow_empty=True)  # No error
        >>> validate_string(None, "text", allow_none=True)  # No error
    """
    if value is None:
        if not allow_none:
            raise TypeError(f"Parameter '{param_name}' must be str, not None")
        return
    
    if not isinstance(value, str):
        raise TypeError(f"Parameter '{param_name}' must be str, got {type(value).__name__}")
    
    if not allow_empty:
        if value == "":
            raise ValueError(f"Parameter '{param_name}' cannot be empty")
        if value.strip() == "":
            raise ValueError(f"Parameter '{param_name}' cannot be only whitespace")


def validate_list(items: Any, param_name: str = "items", allow_empty: bool = False) -> None:
    """
    Validate that a parameter is a list of non-None strings.
    
    Args:
        items: The value to validate as a list
        param_name: Name of the parameter for error messages
        allow_empty: If True, allows empty lists (default: False)
        
    Raises:
        TypeError: If items is None, not a list, or contains non-string items
        ValueError: If items is empty (when allow_empty=False)
        
    Example:
        >>> validate_list(["a", "b"], "items")  # No error
        >>> validate_list([], "items")  # ValueError
        >>> validate_list(["a", None], "items")  # TypeError
    """
    if items is None:
        raise TypeError(f"Parameter '{param_name}' must be a list, not None")
    if not isinstance(items, list):
        raise TypeError(f"Parameter '{param_name}' must be a list, got {type(items).__name__}")
    if not allow_empty and len(items) == 0:
        raise ValueError(f"Parameter '{param_name}' cannot be empty")
    
    # Validate each item is a non-None string
    for i, item in enumerate(items):
        if item is None:
            raise TypeError(f"Parameter '{param_name}[{i}]' cannot be None")
        if not isinstance(item, str):
            raise TypeError(f"Parameter '{param_name}[{i}]' must be str, got {type(item).__name__}")


def validate_image_path(path: Any) -> None:
    """
    Validate that a path points to an existing image file.
    
    Args:
        path: Path to validate (str or Path object)
        
    Raises:
        TypeError: If path is None or not a string/Path
        ValueError: If path is empty
        FileNotFoundError: If file doesn't exist
        ValueError: If file extension is not a valid image format
        
    Example:
        >>> validate_image_path("image.png")  # If file exists
        >>> validate_image_path(Path("image.jpg"))  # If file exists
    """
    if path is None:
        raise TypeError("Parameter 'image_path' must be str, not None")
    
    # Convert Path to string for consistency
    if isinstance(path, Path):
        path = str(path)
    
    # Validate it's a non-empty string
    if path.strip() == "":
        raise ValueError("Parameter 'image_path' cannot be empty")
    
    # Check file exists
    path_obj = Path(path)
    if not path_obj.exists():
        raise FileNotFoundError(f"Image file not found: {path}")
    
    # Check valid extension
    valid_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.svg', '.pdf'}
    if path_obj.suffix.lower() not in valid_extensions:
        raise ValueError(f"Invalid image extension '{path_obj.suffix}'. Must be one of: {', '.join(valid_extensions)}")


def validate_image_width(width: Any) -> None:
    """
    Validate image width specification.
    
    Args:
        width: Width specification (e.g., "50%", "300px")
        
    Raises:
        TypeError: If width is not a string
        ValueError: If format is invalid or value is non-positive
        
    Example:
        >>> validate_image_width("50%")  # No error
        >>> validate_image_width("300px")  # No error
        >>> validate_image_width("-10%")  # ValueError
    """
    if width is None:
        return  # None is allowed (optional parameter)
    
    if not isinstance(width, str):
        raise TypeError(f"Parameter 'width' must be str, got {type(width).__name__}")
    
    # Check format
    if not (width.endswith('%') or width.endswith('px')):
        raise ValueError(f"Parameter 'width' must end with '%' or 'px' (e.g., '80%', '500px')")
    
    # Extract numeric part and validate
    try:
        numeric_str = width[:-2] if width.endswith('px') else width[:-1]
        value = float(numeric_str)
    except ValueError:
        raise ValueError(f"Invalid width format: '{width}'. Must be a number followed by '%' or 'px'")
    
    if value <= 0:
        raise ValueError(f"Parameter 'width' must be positive")


def validate_callout_type(callout_type: Any) -> None:
    """
    Validate callout type parameter.
    
    Args:
        callout_type: The callout type to validate
        
    Raises:
        TypeError: If callout_type is None or not a string
        ValueError: If callout_type is not a valid type
        
    Example:
        >>> validate_callout_type("note")  # No error
        >>> validate_callout_type("invalid")  # ValueError
    """
    if callout_type is None:
        raise TypeError("Parameter 'callout_type' must be str, not None")
    if not isinstance(callout_type, str):
        raise TypeError(f"Parameter 'callout_type' must be str, got {type(callout_type).__name__}")
    
    valid_types = {'note', 'tip', 'warning', 'important', 'caution', 'error', 'success', 'advice'}
    if callout_type.lower() not in valid_types:
        raise ValueError(f"Invalid callout_type '{callout_type}'. Must be one of: {', '.join(valid_types)}")


def validate_reference_key(key: Any) -> None:
    """
    Validate reference key format.
    
    Args:
        key: Reference key to validate
        
    Raises:
        TypeError: If key is None or not a string
        ValueError: If key is empty or has invalid format
        
    Example:
        >>> validate_reference_key("fig_1")  # No error
        >>> validate_reference_key("my-ref")  # No error
        >>> validate_reference_key("invalid key")  # ValueError (contains space)
    """
    if key is None:
        raise TypeError("Parameter 'key' must be str, not None")
    if not isinstance(key, str):
        raise TypeError(f"Parameter 'key' must be str, got {type(key).__name__}")
    if key.strip() == "":
        raise ValueError("Parameter 'key' cannot be empty")
    
    # Check alphanumeric + underscore + hyphen only
    if not re.match(r'^[A-Za-z0-9_-]+$', key):
        raise ValueError(f"Parameter 'key' must be alphanumeric with underscores/hyphens only")


def validate_format(format_value: Any) -> None:
    """
    Validate output format specification.
    
    Args:
        format_value: The format specification to validate
        
    Raises:
        TypeError: If format_value is None or not a string
        ValueError: If format is not supported
        
    Example:
        >>> validate_format("html")  # No error
        >>> validate_format("pdf")  # No error
        >>> validate_format("invalid")  # ValueError
    """
    if format_value is None:
        raise TypeError("Format must be str, not None")
    if not isinstance(format_value, str):
        raise TypeError(f"Format must be str, got {type(format_value).__name__}")
    
    valid_formats = {'html', 'pdf', 'markdown', 'md', 'qmd', 'tex', 'latex'}
    if format_value.lower() not in valid_formats:
        raise ValueError(f"Invalid format '{format_value}'. Must be one of: {', '.join(valid_formats)}")
