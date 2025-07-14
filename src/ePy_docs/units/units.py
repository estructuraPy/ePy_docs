"""Unit detection, extraction, and conversion utilities for engineering data processing."""

import json
import os
import re
from typing import Dict, Union, Any, Optional, List, Tuple
import pandas as pd
from pydantic import BaseModel, Field

# Import from local modules
from ePy_docs.files.data import _load_cached_json, safe_parse_numeric
from ePy_docs.units.converter import _normalize_unit_str, UnitConverter
from ePy_docs.files.mapper import DataFrameColumnMapper



def convert_units_generic(df: pd.DataFrame, 
                         units_info: Dict[str, Dict[str, Any]], 
                         units_mapping: Dict[str, List[str]]) -> pd.DataFrame:
    """Convert units in DataFrame based on units info and mapping.
    
    Args:
        df: DataFrame with columns to convert.
        units_info: Dictionary with unit information from extract_units_info.
        units_mapping: Mapping of columns to unit categories and types.
        
    Returns:
        DataFrame with converted values according to target unit system.
        
    Assumptions:
        Unit converter can handle all specified unit conversions.
        DataFrame contains numeric columns that can be converted.
        User configuration contains valid target unit definitions.    """
    try:
        # Get current project configuration to ensure we use the correct units
        from ePy_docs.project.setup import get_current_project_config
        current_config = get_current_project_config()
        
        # Create UnitConverter with current project configuration
        unit_converter = UnitConverter.create_default(current_config)
        result_df = df.copy()
        
        for col_name, unit_path in units_mapping.items():
            if col_name not in result_df.columns:
                continue
                
            col_type = unit_path[0] if isinstance(unit_path, list) else col_name  
            col_info = units_info.get(col_type, {})
            
            if not col_info or 'raw' not in col_info:
                continue
                
            source_unit = col_info.get('raw')
            if not source_unit:
                continue
                
            target_units = extract_units_info_generic({col_name: unit_path})
            target_unit = target_units.get(col_name)
            
            if target_unit and source_unit != target_unit:
                result_df[col_name] = result_df[col_name].apply(
                    lambda x: unit_converter.universal_unit_converter(
                        x, source_unit, target_unit) if pd.notna(x) else x
                )
        
        return result_df
    except Exception as e:
        raise RuntimeError(f"Error in unit conversion: {e}")


def _get_unit_delimiters_from_config(conversion_file_path: Optional[str] = None) -> Dict[str, List[str]]:
    """Get unit delimiter patterns from configuration file.
    
    Args:
        conversion_file_path: Optional path to conversion JSON file.
        
    Returns:
        Dictionary with delimiter patterns for extracting units from text.
        
    Assumptions:
        Configuration file contains unit_delimiters section with delimiter definitions.
        Fallback delimiters are sufficient when configuration is unavailable.
    """
    if conversion_file_path is None:
        conversion_file_path = os.path.join("templates", "conversion.json")
        if not os.path.exists(conversion_file_path):
            # Use the current package directory
            current_dir = os.path.dirname(os.path.abspath(__file__))
            conversion_file_path = os.path.join(current_dir, "conversion.json")
    
    try:
        conversion_data = _load_cached_json(conversion_file_path)
        
        # Handle case where _load_cached_json returns None
        if conversion_data is None:
            raise FileNotFoundError(f"Could not load conversion data from {conversion_file_path}")
        
        delimiters = conversion_data.get("unit_delimiters", {
            "parentheses": ["(", ")"],
            "brackets": ["[", "]"],
            "braces": ["{", "}"],
            "angle_brackets": ["<", ">"]
        })
        
        return delimiters
    except (FileNotFoundError, Exception) as e:
        raise RuntimeError(f"Could not load unit delimiters from config: {e}")


def extract_units_from_columns(columns: List[str], conversion_file_path: Optional[str] = None) -> Dict[str, str]:
    """Extracts units from column names using delimiter patterns from configuration.

    Args:
        columns: List of column names to process.
        conversion_file_path: Optional path to conversion JSON file.

    Returns:
        Dictionary mapping column names to their extracted units.

    Assumptions:
        Column names follow standard engineering notation with units in delimiters.
        Nested delimiters are handled by finding the last occurrence.
        Empty units are filtered out from results.
    """
    delimiters = _get_unit_delimiters_from_config(conversion_file_path)
    units = {}

    for col in columns:
        for delimiter_type, (open_char, close_char) in delimiters.items():
            if open_char in col and close_char in col:
                open_pos = col.rfind(open_char)
                close_pos = col.find(close_char, open_pos)

                if open_pos != -1 and close_pos != -1 and close_pos > open_pos:
                    unit = col[open_pos + 1:close_pos].strip()
                    if unit:
                        units[col] = unit
                        break  # Exit inner loop once a unit is found
    return units


def extract_units_info_generic(df_or_dict: pd.DataFrame, column_mapper: DataFrameColumnMapper, element_type: str, conversion_file_path: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
    """Extracts unit information from DataFrame column headers or dictionary.

    Args:
        df_or_dict: DataFrame with column headers containing unit information or dictionary mapping column names to units.
        column_mapper: RobotColumnMapper instance for column type mapping.
        element_type: Type of structural element (e.g., "Frames", "Nodes").
        conversion_file_path: Optional path to conversion JSON file.

    Returns:
        Dictionary with processed unit information for each component.

    Assumptions:
        Column mapper can identify component types from column names.
        Unit detection successfully extracts meaningful unit strings.
        Unit type detection provides valid categorization.
    """
    units_info = {}

    if hasattr(df_or_dict, 'columns'):
        column_units = extract_units_from_columns(df_or_dict.columns, conversion_file_path)
    else:
        column_units = df_or_dict

    for col, unit in column_units.items():
        col_type = column_mapper.get_column_type(str(col), element_type)
        if col_type and unit:
            units_info[col_type] = {
                'raw': unit,
                'info': detect_unit_type(unit, conversion_file_path)
            }
    return units_info


def _get_prefixes_from_config(prefix_file_path: Optional[str] = None) -> List[str]:
    """Get SI prefixes from configuration file.
    
    Args:
        prefix_file_path: Optional path to prefix JSON file.
        
    Returns:
        List of prefix symbols from configuration.
        
    Raises:
        FileNotFoundError: If prefix configuration file cannot be loaded.
        
    Assumptions:
        Prefix file contains multiples and submultiples sections with symbol definitions.
        Configuration structure follows expected format for prefix data.
    """
    if prefix_file_path is None:
        prefix_file_path = os.path.join("templates", "prefix.json")
        if not os.path.exists(prefix_file_path):
            # Fix: Use the correct import
            package_dir = os.path.dirname(os.path.abspath(ePy_docs.__file__))
            prefix_file_path = os.path.join(package_dir, "units", "prefix.json")
    
    try:
        prefix_data = _load_cached_json(prefix_file_path)
        
        # Handle case where _load_cached_json returns None
        if prefix_data is None:
            print(f"Warning: Could not load prefix data from {prefix_file_path}")
            return ['k', 'M', 'G', 'm', 'μ', 'n']  # Basic fallback prefixes
            
    except (FileNotFoundError, Exception) as e:
        print(f"Warning: Could not load prefixes from config: {e}")
        return ['k', 'M', 'G', 'm', 'μ', 'n']  # Basic fallback prefixes
    
    prefixes = []
    
    prefix_info = prefix_data.get("prefix", {})
    
    multiples = prefix_info.get("multiples", {})
    for prefix_name, info in multiples.items():
        if "symbol" in info:
            prefixes.append(info["symbol"])
    
    submultiples = prefix_info.get("submultiples", {})
    for prefix_name, info in submultiples.items():
        if "symbol" in info:
            prefixes.append(info["symbol"])
    
    return prefixes if prefixes else ['k', 'M', 'G', 'm', 'μ', 'n']


def detect_unit_type(unit_str: str, conversion_file_path: Optional[str] = None) -> Dict[str, Any]:
    """Detect unit type by searching conversion.json categories.

    Args:
        unit_str: String representation of the unit.
        conversion_file_path: Optional path to conversion JSON file.

    Returns:
        Dictionary with unit properties containing 'type' and 'unit' keys.
        
    Assumptions:
        Conversion file contains categories with conversion matrices.
        Unit normalization handles case and format variations consistently.
        Unknown units are handled gracefully with appropriate type marking.
    """
    if conversion_file_path is None:
        conversion_file_path = os.path.join("templates", "conversion.json")
        if not os.path.exists(conversion_file_path):
            # Use the current package directory
            current_dir = os.path.dirname(os.path.abspath(__file__))
            conversion_file_path = os.path.join(current_dir, "conversion.json")
    
    try:
        conversion_data = _load_cached_json(conversion_file_path)
        
        # Handle case where _load_cached_json returns None
        if conversion_data is None:
            print(f"Warning: Could not load conversion data from {conversion_file_path}")
            return {"type": "unknown", "unit": unit_str}
            
    except (FileNotFoundError, Exception) as e:
        print(f"Warning: Could not load conversion data: {e}")
        return {"type": "unknown", "unit": unit_str}
    
    unit_norm = _normalize_unit_str(unit_str.lower())
    categories = conversion_data.get("categories", {})
    
    for category_name, category_data in categories.items():
        if not isinstance(category_data, dict):
            continue
            
        conversions = category_data.get("conversions", {})
        if not isinstance(conversions, dict):
            continue
            
        for base_unit in conversions.keys():
            if unit_norm == _normalize_unit_str(base_unit.lower()):
                return {"type": category_name, "unit": base_unit}
                
        for base_unit, unit_conversions in conversions.items():
            if isinstance(unit_conversions, dict):
                for target_unit in unit_conversions.keys():
                    if not target_unit.startswith("offset_"):
                        if unit_norm == _normalize_unit_str(target_unit.lower()):
                            return {"type": category_name, "unit": target_unit}
    
    return {"type": "unknown", "unit": unit_str}


def convert_to_default_units(df: pd.DataFrame, column_units: Dict[str, str]) -> Tuple[pd.DataFrame, Dict[str, str]]:
    """Convert DataFrame columns to units from units.json configuration.
    
    Args:
        df: DataFrame with data to convert.
        column_units: Dictionary mapping column names to their current units.
        
    Returns:
        Tuple of (converted_dataframe, conversion_log).
        
    Raises:
        FileNotFoundError: If units.json configuration file is not found.
        
    Assumptions:
        Units configuration file exists in templates directory.
        UnitConverter can handle all required unit conversions.
        Column headers can be safely modified to include target units.    """
    # Get current project configuration to use the correct units files
    from ePy_docs.project.setup import get_current_project_config
    current_config = get_current_project_config()
    
    # Create converter using current project configuration
    if current_config:
        # Using project config for unit conversion
        converter = UnitConverter.create_default(current_config)
    else:
        # Fallback to library files if no project config
        package_dir = os.path.dirname(os.path.abspath(ePy_docs.__file__))
        conversion_path = os.path.join(package_dir, "units", "conversion.json")
        prefix_path = os.path.join(package_dir, "units", "prefix.json")
        aliases_path = os.path.join(package_dir, "units", "aliases.json")        
        converter = UnitConverter.from_file(
            units_file_path=conversion_path,
            prefix_file_path=prefix_path,
            aliases_file_path=aliases_path
        )
    
    converted_df = df.copy()
    conversion_log = {}
    
    # Use the current project configuration to get the units config
    if current_config:
        units_config = current_config.load_config_file('units')
        # Units config loaded silently
    else:
        # Fallback to library units.json
        package_dir = os.path.dirname(os.path.abspath(ePy_docs.__file__))
        units_config_path = os.path.join(package_dir, "units", "units.json")
        
        if not os.path.exists(units_config_path):
            print(f"Warning: units.json not found at {units_config_path}")
            return df, {"error": "units.json not found"}
        
        try:
            units_config = _load_cached_json(units_config_path)
            print(f"⚠️ Using fallback units config from library: {units_config_path}")
        except Exception as e:
            raise RuntimeError(f"Could not load units configuration: {e}")
    
    # Handle case where units_config is None
    if units_config is None:
        raise RuntimeError("Could not load units configuration")
    
    categories = units_config.get("categories", {})
    
    # Build target_units_config with priority for structure_dimensions to avoid conflicts
    # where multiple categories define the same unit_type (e.g., "length")
    target_units_config = {}
    
    # Define priority order - structure_dimensions comes first and has highest priority
    priority_categories = [
        "structure_dimensions",  # Highest priority for main structural dimensions
        "forces", 
        "displacements",
        "temperature",
        "angles",
        "stress",
        "section_dimensions",  # Lower priority - should not override structure_dimensions
        "stiffness",
        "time_related",
        "mass_and_weight",
        "modal_factors",
        "damping_items",
        "miscellaneous"
    ]
    
    # Process categories in priority order (later ones don't overwrite earlier ones)
    for category_name in priority_categories:
        if category_name in categories:
            category_data = categories[category_name]
            if isinstance(category_data, dict):
                for unit_type, unit_list in category_data.items():
                    if unit_type != "description" and isinstance(unit_list, list) and unit_list:
                        # Only set if not already set (priority system)
                        if unit_type not in target_units_config:
                            # Normalize unit using aliases system
                            normalized_unit = converter._normalize_unit_with_aliases(unit_list[0])
                            target_units_config[unit_type] = normalized_unit
    
    # Process any remaining categories not in priority list
    for category_name, category_data in categories.items():
        if category_name not in priority_categories and isinstance(category_data, dict):
            for unit_type, unit_list in category_data.items():
                if unit_type != "description" and isinstance(unit_list, list) and unit_list:
                    if unit_type not in target_units_config:
                        # Normalize unit using aliases system
                        normalized_unit = converter._normalize_unit_with_aliases(unit_list[0])
                        target_units_config[unit_type] = normalized_unit
    
    # Target units configuration created silently
    
    column_renames = {}
    for col_name, current_unit in column_units.items():
        if col_name not in df.columns:
            continue
            
        # Normalize unit using aliases system for consistent display
        current_unit_display = converter._normalize_unit_with_aliases(current_unit)
        
        unit_info = detect_unit_type(current_unit)
        unit_category = unit_info.get("type", "unknown")
        
        # Unit detection performed silently
        
        if unit_category == "unknown":
            conversion_log[col_name] = f"{current_unit} (unknown type)"
            continue
        
        target_unit = target_units_config.get(unit_category)
        if not target_unit:
            conversion_log[col_name] = f"{current_unit} (no target configured)"
            continue
        
        # Target unit determination performed silently
        
        base_col_name = col_name
        if '(' in col_name and ')' in col_name:
            base_col_name = col_name[:col_name.find('(')].strip()
        
        current_unit_norm = _normalize_unit_str(current_unit)
        target_unit_norm = _normalize_unit_str(target_unit)
        
        if current_unit_norm.lower() == target_unit_norm.lower():
            new_col_name = f"{base_col_name} ({target_unit})"
            if new_col_name != col_name:
                column_renames[col_name] = new_col_name
            conversion_log[col_name] = f"{current_unit} (no conversion needed)"
            continue
        
        try:
            test_result = converter.universal_unit_converter(1.0, current_unit, target_unit)
            
            if isinstance(test_result, str):
                print(f"Conversion failed: {current_unit} -> {target_unit}: {test_result}")
                conversion_log[col_name] = f"{current_unit} (conversion failed)"
                continue
            
            print(f"Conversion successful: {current_unit} -> {target_unit} (factor: {test_result})")
            
            converted_df[col_name] = df[col_name].apply(
                lambda x: converter.universal_unit_converter(float(x), current_unit, target_unit) 
                if pd.notna(x) and x != '' else x
            )
            
            new_col_name = f"{base_col_name} ({target_unit})"
            column_renames[col_name] = new_col_name
            
            conversion_log[col_name] = f"{current_unit} -> {target_unit}"
            
        except Exception as e:
            print(f"Error during conversion: {e}")
            conversion_log[col_name] = f"{current_unit} (error)"
            continue
    
    if column_renames:
        converted_df = converted_df.rename(columns=column_renames)
        # Update conversion log with new column names
        updated_log = {}
        for old_name, log_entry in conversion_log.items():
            new_name = column_renames.get(old_name, old_name)
            updated_log[new_name] = log_entry
        conversion_log = updated_log
    
    return converted_df, conversion_log


def auto_detect_and_convert_units(df: pd.DataFrame, conversion_file_path: Optional[str] = None) -> Tuple[pd.DataFrame, Dict[str, str]]:
    """Automatically detect units from column names and convert to default units.
    
    Args:
        df: DataFrame with column names containing unit information.
        conversion_file_path: Optional path to conversion file.
        
    Returns:
        Tuple of (converted_dataframe, conversion_log).
        
    Assumptions:
        Column names contain extractable unit information.
        Default unit conversion can be performed for detected units.
        Units configuration is available in expected location.
    """
    column_units = extract_units_from_columns(df.columns.tolist(), conversion_file_path)
    
    if not column_units:
        print("No units detected in column names")
        return df, {}

    converted_dataframe, conversion_log = convert_to_default_units(df, column_units)
    
    return converted_dataframe, conversion_log



def extract_units_from_dataframe_columns(df: pd.DataFrame) -> Dict[str, str]:
    """Extract unit information from DataFrame column headers.
    
    Args:
        df: DataFrame with columns potentially containing unit information.
        
    Returns:
        Dictionary mapping column names to their extracted units.
        
    Assumptions:
        Units are enclosed in parentheses or brackets in column names.
    """
    units_dict = {}
    
    # Regex patterns to extract units from column names
    unit_patterns = [
        r'\(([^)]+)\)',  # Matches units in parentheses: X (m)
        r'\[([^\]]+)\]',  # Matches units in brackets: X [m]
        r'_([a-zA-Z0-9°/]+)$'  # Matches units after underscore: X_m
    ]
    
    for col in df.columns:
        col_name = str(col)
        for pattern in unit_patterns:
            match = re.search(pattern, col_name)
            if match:
                unit = match.group(1).strip()
                base_col_name = re.sub(pattern, '', col_name).strip()
                units_dict[col_name] = unit
                break
    
    return units_dict


def process_dataframe_with_units(df: pd.DataFrame, 
                                 preserve_node_column: bool = True, 
                                 node_column: str = 'Node',
                                 convert_to_target_units: bool = True) -> pd.DataFrame:
    """Process DataFrame to ensure node numbers are preserved and units are converted.
    
    Args:
        df: DataFrame to process
        preserve_node_column: Whether to preserve the node column as index
        node_column: Name of the node column
        convert_to_target_units: Whether to convert units to target units
        
    Returns:
        Processed DataFrame with preserved node column and converted units
        
    Assumptions:
        Node column exists in the DataFrame
        Units are properly specified in column headers
    """
    # Make a copy to avoid modifying the original
    result_df = df.copy()
    
    # Ensure node_column is first and preserved
    if node_column in result_df.columns:
        # Convert node column to string and ensure it's not lost during processing
        result_df[node_column] = result_df[node_column].astype(str)
        
        # If preserve_node_column is True, set node column as index
        if preserve_node_column:
            result_df = result_df.set_index(node_column)
    
    # Extract units from column names
    units_dict = extract_units_from_dataframe_columns(result_df)
    
    if convert_to_target_units and units_dict:
        from ePy_docs.units.converter import UnitConverter
        from ePy_docs.units.units import get_target_units_from_user_config
        
        # Create mapping for unit conversion
        units_mapping = {}
        for col, unit in units_dict.items():
            # Determine category based on column name and unit
            if any(dim in col.lower() for dim in ['x', 'y', 'z']):
                units_mapping[col] = ['structure_dimensions', 'length']
            elif 'force' in col.lower():
                units_mapping[col] = ['forces', 'force']
            elif 'moment' in col.lower():
                units_mapping[col] = ['forces', 'moment']
            else:
                # Default to structure dimensions for unrecognized columns with units
                units_mapping[col] = ['structure_dimensions', 'length']
        
        # Get target units from configuration
        target_units = get_target_units_from_user_config(units_mapping)
          # Convert units using the same approach as convert_units_generic
        if target_units:
            from ePy_docs.project.setup import get_current_project_config
            current_config = get_current_project_config()
            
            if current_config:
                unit_converter = UnitConverter.create_default(current_config)
            else:
                unit_converter = UnitConverter.create_default()
            
            for col_name, target_unit in target_units.items():
                if col_name not in result_df.columns:
                    continue
                
                # Extract the source unit from the column name
                units_dict = extract_units_from_dataframe_columns(result_df)
                source_unit = units_dict.get(col_name)
                
                if source_unit and source_unit != target_unit:
                    print(f"🔄 Converting column '{col_name}' from '{source_unit}' to '{target_unit}'")
                    result_df[col_name] = result_df[col_name].apply(
                        lambda x: unit_converter.universal_unit_converter(
                            x, source_unit, target_unit) if pd.notna(x) else x
                    )
    
    return result_df


def convert_numeric_with_comma_decimal(df: pd.DataFrame) -> pd.DataFrame:
    """Convert numeric columns with comma decimal separator to standard format.
    
    Args:
        df: DataFrame with potential comma decimal notation
        
    Returns:
        DataFrame with properly converted numeric columns
        
    Assumptions:
        Columns with comma as decimal separator can be identified
        Numeric columns should be converted to float type
    """
    result_df = df.copy()
    
    # Identify columns that might contain numeric values with comma
    for col in result_df.columns:
        # Skip columns that are already numeric
        if pd.api.types.is_numeric_dtype(result_df[col]):
            continue
            
        # Check if column values contain numbers with comma decimal separators
        if result_df[col].astype(str).str.match(r'\s*-?\d+,\d+\s*').any():
            # Convert comma to dot and to numeric
            result_df[col] = result_df[col].astype(str).str.replace(',', '.').astype(float)
    
    return result_df


def get_target_units_from_user_config(units_mapping: Dict[str, List[str]]) -> Dict[str, str]:
    """Get target units from user configuration based on column mapping.
    
    Args:
        units_mapping: Dictionary mapping column names to [category, subcategory] lists
        
    Returns:
        Dictionary mapping column names to target unit strings
        
    Assumptions:
        User configuration is properly loaded and accessible
        Categories and subcategories exist in user configuration
    """
    from ePy_docs.project.setup import get_current_project_config
    
    target_units = {}
    
    try:
        # Get current project configuration to ensure we use the correct units
        current_config = get_current_project_config()
        
        if current_config:
            print(f"🔧 get_target_units_from_user_config using config: {current_config.folders.config}")
            
            # Load the units.json file to get the target unit categories
            units_config = current_config.load_config_file('units')
            
            if not units_config:
                print("❌ get_target_units_from_user_config: No units config available")
                return target_units
            
            categories = units_config.get('categories', {})
            
            for col_name, mapping in units_mapping.items():
                if len(mapping) >= 2:
                    category = mapping[0]  # e.g., 'structure_dimensions'
                    subcategory = mapping[1]  # e.g., 'length'
                    
                    # Get the target unit from configuration
                    if category in categories and subcategory in categories[category]:
                        unit_list = categories[category][subcategory]
                        if isinstance(unit_list, list) and len(unit_list) > 0:
                            target_unit = unit_list[0]  # Take the first unit as target
                            target_units[col_name] = target_unit
                            print(f"🎯 Target unit for '{col_name}' ({category}→{subcategory}): '{target_unit}'")
                        else:
                            print(f"⚠️ Empty or invalid unit list for {category}→{subcategory}")
                    else:
                        print(f"⚠️ Category {category}→{subcategory} not found in units config")
                        # Debug: show available categories
                        if category in categories:
                            print(f"   Available subcategories in {category}: {list(categories[category].keys())}")
                        else:
                            print(f"   Available categories: {list(categories.keys())}")
                else:
                    print(f"⚠️ Invalid mapping for column {col_name}: {mapping}")
        else:
            print("⚠️ get_target_units_from_user_config: No current project config found, using default")
    
    except Exception as e:
        print(f"❌ Error in get_target_units_from_user_config: {e}")
    
    return target_units

