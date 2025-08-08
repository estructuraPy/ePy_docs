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
    """
    from ePy_docs.project.setup import get_current_project_config
    current_config = get_current_project_config()
    
    if not current_config:
        raise RuntimeError("No project configuration found")
    
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


def _get_unit_delimiters_from_config(conversion_file_path: Optional[str] = None) -> Dict[str, List[str]]:
    """Get unit delimiter patterns from configuration file.
    
    Args:
        conversion_file_path: Optional path to conversion JSON file.
        
    Returns:
        Dictionary with delimiter patterns for extracting units from text.
    """
    if conversion_file_path is None:
        from ePy_docs.project.setup import get_current_project_config
        current_config = get_current_project_config()
        
        if current_config is None:
            raise RuntimeError("No project configuration available and no conversion_file_path provided")
        
        # Use dynamic configuration path
        conversion_file_path = current_config.files.configuration.units.conversion_json
    
    conversion_data = _load_cached_json(conversion_file_path)
    
    if conversion_data is None:
        raise FileNotFoundError(f"Could not load conversion data from {conversion_file_path}")
    
    delimiters = conversion_data.get("unit_delimiters")
    if delimiters is None:
        raise KeyError(f"unit_delimiters section not found in {conversion_file_path}")
        
    return delimiters


def extract_units_from_columns(columns: List[str], conversion_file_path: Optional[str] = None) -> Dict[str, str]:
    """Extracts units from column names using delimiter patterns from configuration.

    Args:
        columns: List of column names to process.
        conversion_file_path: Optional path to conversion JSON file.

    Returns:
        Dictionary mapping column names to their extracted units.
    """
    delimiters = _get_unit_delimiters_from_config(conversion_file_path)
    units = {}
    
    # Common unit patterns without delimiters - using proper formatting
    unit_patterns = {
        'kgfcm': 'kgf·cm',
        'kgfm': 'kgf·m',
        'tonm': 'ton·m',
        'tonfm': 'tonf·m',
        'lbfft': 'lbf·ft',
        'lbfin': 'lbf·in',
        'kipft': 'kip·ft',
        'kipin': 'kip·in',
        'nm': 'N·m',
        'knm': 'kN·m',
        'mnm': 'MN·m',
    }

    for col in columns:
        found_unit = None
        
        # First try delimiter-based extraction
        for delimiter_type, (open_char, close_char) in delimiters.items():
            if open_char in col and close_char in col:
                open_pos = col.rfind(open_char)
                close_pos = col.find(close_char, open_pos)

                if open_pos != -1 and close_pos != -1 and close_pos > open_pos:
                    unit = col[open_pos + 1:close_pos].strip()
                    if unit:
                        found_unit = unit
                        break
        
        # If no unit found with delimiters, try pattern matching on full column name
        if found_unit is None:
            col_lower = col.lower()
            # Sort patterns by length (longest first) to avoid partial matches
            sorted_patterns = sorted(unit_patterns.items(), key=lambda x: len(x[0]), reverse=True)
            for pattern, standard_unit in sorted_patterns:
                if col_lower.endswith(pattern):
                    found_unit = standard_unit
                    break
        
        # Apply pattern corrections to found unit (whether from delimiters or patterns)
        if found_unit:
            # Only apply corrections if the unit wasn't already processed by pattern matching
            if found_unit not in unit_patterns.values():
                corrected_unit = unit_patterns.get(found_unit.lower(), found_unit)
                units[col] = corrected_unit
            else:
                units[col] = found_unit
                    
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


# def _get_prefixes_from_config(prefix_file_path: str) -> List[str]:
#     """Get SI prefixes from configuration file.
    
#     Args:
#         prefix_file_path: Path to prefix JSON file.
        
#     Returns:
#         List of prefix symbols from configuration.
#     """
#     prefix_data = _load_cached_json(prefix_file_path)
    
#     if prefix_data is None:
#         raise FileNotFoundError(f"Could not load prefix data from {prefix_file_path}")
            
#     prefixes = []
#     prefix_info = prefix_data.get("prefix", {})
    
#     multiples = prefix_info.get("multiples", {})
#     for prefix_name, info in multiples.items():
#         if "symbol" in info:
#             prefixes.append(info["symbol"])
    
#     submultiples = prefix_info.get("submultiples", {})
#     for prefix_name, info in submultiples.items():
#         if "symbol" in info:
#             prefixes.append(info["symbol"])
    
#     if not prefixes:
#         raise ValueError(f"No valid prefixes found in {prefix_file_path}")
    
#     return prefixes


def detect_unit_type(unit_str: str, conversion_file_path: Optional[str] = None) -> Dict[str, Any]:
    """Detect unit type by searching conversion.json categories.

    Args:
        unit_str: String representation of the unit.
        conversion_file_path: Optional path to conversion JSON file.

    Returns:
        Dictionary with unit properties containing 'type' and 'unit' keys.
    """
    if conversion_file_path is None:
        from ePy_docs.project.setup import get_current_project_config
        current_config = get_current_project_config()
        
        if current_config is None:
            raise RuntimeError("No project configuration available and no conversion_file_path provided")
        
        # Use dynamic configuration path  
        conversion_file_path = current_config.files.configuration.units.conversion_json
    
    conversion_data = _load_cached_json(conversion_file_path)
    
    if conversion_data is None:
        raise FileNotFoundError(f"Could not load conversion data from {conversion_file_path}")
    
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
    """
    from ePy_docs.project.setup import get_current_project_config
    current_config = get_current_project_config()
    
    if not current_config:
        raise RuntimeError("No project configuration found")
    
    converter = UnitConverter.create_default(current_config)
    converted_df = df.copy()
    conversion_log = {}
    
    units_config = current_config.load_config_file('units')
    if units_config is None:
        raise RuntimeError("Could not load units configuration")
    
    categories = units_config.get("categories", {})
    
    # Build target_units_config with priority for structure_dimensions
    target_units_config = {}
    
    priority_categories = [
        "structure_dimensions",
        "forces", 
        "displacements",
        "temperature",
        "angles",
        "stress",
        "section_dimensions",
        "stiffness",
        "time_related",
        "mass_and_weight",
        "modal_factors",
        "damping_items",
        "miscellaneous"
    ]
    
    # Process categories in priority order
    for category_name in priority_categories:
        if category_name in categories:
            category_data = categories[category_name]
            if isinstance(category_data, dict):
                for unit_type, unit_list in category_data.items():
                    if unit_type != "description" and isinstance(unit_list, list) and unit_list:
                        if unit_type not in target_units_config:
                            normalized_unit = converter._normalize_unit_with_aliases(unit_list[0])
                            target_units_config[unit_type] = normalized_unit
    
    # Process remaining categories
    for category_name, category_data in categories.items():
        if category_name not in priority_categories and isinstance(category_data, dict):
            for unit_type, unit_list in category_data.items():
                if unit_type != "description" and isinstance(unit_list, list) and unit_list:
                    if unit_type not in target_units_config:
                        normalized_unit = converter._normalize_unit_with_aliases(unit_list[0])
                        target_units_config[unit_type] = normalized_unit
    
    column_renames = {}
    for col_name, current_unit in column_units.items():
        if col_name not in df.columns:
            continue
            
        current_unit_display = converter._normalize_unit_with_aliases(current_unit)
        
        conversion_file_path = current_config.files.configuration.units.conversion_json
        unit_info = detect_unit_type(current_unit, conversion_file_path)
        unit_category = unit_info.get("type", "unknown")
        
        if unit_category == "unknown":
            conversion_log[col_name] = f"{current_unit} (unknown type)"
            continue
        
        target_unit = target_units_config.get(unit_category)
        if not target_unit:
            conversion_log[col_name] = f"{current_unit} (no target configured)"
            continue
        
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
                conversion_log[col_name] = f"{current_unit} (conversion failed: {test_result})"
                continue
            
            converted_df[col_name] = df[col_name].apply(
                lambda x: converter.universal_unit_converter(float(x), current_unit, target_unit) 
                if pd.notna(x) and x != '' else x
            )
            
            new_col_name = f"{base_col_name} ({target_unit})"
            column_renames[col_name] = new_col_name
            
            conversion_log[col_name] = f"{current_unit} -> {target_unit}"
            
        except Exception as e:
            conversion_log[col_name] = f"{current_unit} (error: {str(e)})"
            continue
    
    if column_renames:
        converted_df = converted_df.rename(columns=column_renames)
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
    """
    column_units = extract_units_from_columns(df.columns.tolist(), conversion_file_path)
    
    if not column_units:
        raise ValueError("No units detected in column names")

    converted_dataframe, conversion_log = convert_to_default_units(df, column_units)
    
    return converted_dataframe, conversion_log



def extract_units_from_dataframe_columns(df: pd.DataFrame) -> Dict[str, str]:
    """Extract unit information from DataFrame column headers.
    
    Args:
        df: DataFrame with columns potentially containing unit information.
        
    Returns:
        Dictionary mapping column names to their extracted units.
    """
    units_dict = {}
    
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
    """
    result_df = df.copy()
    
    if node_column in result_df.columns:
        result_df[node_column] = result_df[node_column].astype(str)
        
        if preserve_node_column:
            result_df = result_df.set_index(node_column)
    
    units_dict = extract_units_from_dataframe_columns(result_df)

    if convert_to_target_units and units_dict:
        from ePy_docs.units.converter import UnitConverter
        from ePy_docs.project.setup import get_current_project_config

        current_config = get_current_project_config()
        if not current_config:
            raise RuntimeError("No project configuration found")

        # Obtener el mapping de columnas a categorías/subcategorías solo del JSON de unidades
        units_config = current_config.load_config_file('units')
        if not units_config:
            raise RuntimeError("No units config available")

        categories = units_config.get('categories', {})
        units_mapping = {}
        for col in units_dict:
            # Buscar el mapping de la columna en el JSON (por nombre exacto)
            found = False
            for cat, subcats in categories.items():
                if not isinstance(subcats, dict):
                    continue
                for subcat, unit_list in subcats.items():
                    if subcat == 'description':
                        continue
                    # Si la columna está listada explícitamente en la subcategoría
                    if isinstance(unit_list, list) and col in unit_list:
                        units_mapping[col] = [cat, subcat]
                        found = True
                        break
                if found:
                    break
        if not units_mapping:
            # Si no hay mapping explícito, no se realiza conversión
            return result_df

        # TODO: Implement get_target_units_from_user_config function
        # target_units = get_target_units_from_user_config(units_mapping)
        target_units = {}  # Temporary fix

        if target_units:
            unit_converter = UnitConverter.create_default(current_config)
            for col_name, target_unit in target_units.items():
                if col_name not in result_df.columns:
                    continue
                units_dict = extract_units_from_dataframe_columns(result_df)
                source_unit = units_dict.get(col_name)
                if source_unit and source_unit != target_unit:
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
    """
    result_df = df.copy()
    
    for col in result_df.columns:
        if pd.api.types.is_numeric_dtype(result_df[col]):
            continue
            
        if result_df[col].astype(str).str.match(r'\s*-?\d+,\d+\s*').any():
            result_df[col] = result_df[col].astype(str).str.replace(',', '.').astype(float)
    
    return result_df


# def get_target_units_from_user_config(units_mapping: Dict[str, List[str]]) -> Dict[str, str]:
#     """Get target units from user configuration based on column mapping.
    
#     Args:
#         units_mapping: Dictionary mapping column names to [category, subcategory] lists
        
#     Returns:
#         Dictionary mapping column names to target unit strings
#     """
#     from ePy_docs.project.setup import get_current_project_config
    
#     target_units = {}
#     current_config = get_current_project_config()
    
#     if not current_config:
#         raise RuntimeError("No project configuration found")
    
#     units_config = current_config.load_config_file('units')
#     if not units_config:
#         raise RuntimeError("No units config available")
    
#     categories = units_config.get('categories', {})
    
#     for col_name, mapping in units_mapping.items():
#         if len(mapping) >= 2:
#             category = mapping[0]
#             subcategory = mapping[1]
            
#             if category in categories and subcategory in categories[category]:
#                 unit_list = categories[category][subcategory]
#                 if isinstance(unit_list, list) and len(unit_list) > 0:
#                     target_unit = unit_list[0]
#                     target_units[col_name] = target_unit
#                 else:
#                     raise ValueError(f"Empty or invalid unit list for {category}→{subcategory}")
#             else:
#                 available_cats = list(categories.keys()) if category not in categories else list(categories[category].keys())
#                 raise KeyError(f"Category {category}→{subcategory} not found. Available: {available_cats}")
#         else:
#             raise ValueError(f"Invalid mapping for column {col_name}: {mapping}")
    
#     return target_units

