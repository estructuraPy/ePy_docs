"""
Pure file reading utilities for ePy_docs FILES world.

Direct file operations without class overhead or verbose contamination.
TRANSPARENCY DIMENSION: Silent operations, no fallbacks, halt-on-failure.
"""

import os
import re
import json
from typing import List, Any, Dict, Optional
from functools import lru_cache
from pathlib import Path

import pandas as pd
from pydantic import BaseModel, Field

from .data import _load_cached_files


@lru_cache(maxsize=1)
def _load_reader_config() -> Dict[str, Any]:
    """Load reader configuration from JSON file."""
    config_path = Path(__file__).parent / "reader.json"
    if not config_path.exists():
        raise FileNotFoundError(f"Reader configuration file not found: {config_path}")
    
    return _load_cached_files(str(config_path), sync_files=False)


def _load_setup_config(sync_files: bool = True) -> Dict[str, Any]:
    """Load configuration from setup.json file using the project configuration manager."""
    from .data import _load_cached_files
    from ePy_docs.components.setup import _resolve_config_path
    config_path = _resolve_config_path('components/setup', sync_files)
    return _load_cached_files(config_path, sync_files)


# PURE FUNCTIONS - TRANSPARENCY DIMENSION COMPLIANT

def load_json_file(file_path: str) -> Dict[str, Any]:
    """Load JSON file with pure operations and halt-on-failure.
    
    Args:
        file_path: Path to JSON file
        
    Returns:
        Dictionary containing JSON data
        
    Raises:
        FileNotFoundError: If file does not exist
        ValueError: If file is empty or has invalid JSON
        RuntimeError: If file cannot be read
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"JSON file not found: {file_path}")
        
    if os.path.getsize(file_path) == 0:
        raise ValueError(f"JSON file is empty: {file_path}")
    
    try:
        return _load_cached_files(file_path)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format in {file_path}: {e}")
    except Exception as e:
        raise RuntimeError(f"Error reading JSON {file_path}: {e}")


def load_text_file(file_path: str) -> str:
    """Load text file with pure operations and halt-on-failure.
    
    Args:
        file_path: Path to text file
        
    Returns:
        String content of the file
        
    Raises:
        FileNotFoundError: If file does not exist
        RuntimeError: If file cannot be read
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Text file not found: {file_path}")
        
    if os.path.getsize(file_path) == 0:
        return ""  # Empty file is valid for text
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        # Try with latin-1 encoding
        try:
            with open(file_path, 'r', encoding='latin-1') as f:
                return f.read()
        except Exception as e:
            raise RuntimeError(f"Error reading text file {file_path}: {e}")
    except Exception as e:
        raise RuntimeError(f"Error reading text file {file_path}: {e}")


def clean_dataframe_bom(df: pd.DataFrame) -> pd.DataFrame:
    """Remove BOM (Byte Order Mark) from DataFrame column names.
    
    Args:
        df: DataFrame with potentially BOM-affected column names
        
    Returns:
        DataFrame with cleaned column names
    """
    if df.empty:
        return df
        
    reader_config = _load_reader_config()
    bom_chars = reader_config["bom_characters"]
    cleaned_columns = []
    
    for col in df.columns:
        if isinstance(col, str):
            cleaned_col = col
            for bom_char in bom_chars:
                cleaned_col = cleaned_col.lstrip(bom_char)
            cleaned_columns.append(cleaned_col.strip())
        else:
            cleaned_columns.append(col)
    
    df.columns = cleaned_columns
    return df


def detect_csv_separator(file_path: str) -> Optional[str]:
    """Detect CSV separator by analyzing file content with encoding detection.
    
    Args:
        file_path: Path to CSV file
        
    Returns:
        Most likely separator or None if detection fails
    """
    reader_config = _load_reader_config()
    encodings_to_try = reader_config["encoding"]["separator_detection"]
    sample_lines_count = reader_config["csv_detection"]["sample_lines_separator"]
    
    for encoding in encodings_to_try:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                sample_lines = f.readlines()[:sample_lines_count]
            break
        except UnicodeDecodeError:
            continue
    else:
        return None
    
    if not sample_lines:
        return None
    
    separators = reader_config["csv_detection"]["separators"]
    separator_counts = {}
    
    for sep in separators:
        separator_counts[sep] = sum(line.count(sep) for line in sample_lines)
    
    if separator_counts:
        detected_sep = max(separator_counts, key=separator_counts.get)
        if separator_counts[detected_sep] > 0:
            return detected_sep
    
    return None


def detect_csv_header_row(file_path: str) -> int:
    """Detect the header row in CSV files by looking for text patterns.
    
    Args:
        file_path: Path to CSV file
        
    Returns:
        Row number containing the header (0-based index)
    """
    reader_config = _load_reader_config()
    encodings_to_try = reader_config["encoding"]["header_detection"]
    sample_rows = reader_config["csv_detection"]["sample_rows"]
    default_separator = reader_config["csv_detection"]["default_separator"]
    text_threshold = reader_config["csv_detection"]["text_threshold"]
    
    for encoding in encodings_to_try:
        try:
            sample_df = pd.read_csv(file_path, sep=default_separator, nrows=sample_rows, 
                                  header=None, encoding=encoding)
            
            for idx, row in sample_df.iterrows():
                text_count = sum(1 for val in row if isinstance(val, str) and 
                               not str(val).replace('.', '').replace(',', '').replace('-', '').isdigit())
                if text_count > len(row) * text_threshold:
                    return idx
            return 0
        except (UnicodeDecodeError, pd.errors.EmptyDataError):
            continue
        except Exception:
            return 0
    
    return 0


def load_csv_file(file_path: str, sync_files: bool = True, **kwargs) -> pd.DataFrame:
    """Load CSV file with pure operations and halt-on-failure.
    
    Args:
        file_path: Path to CSV file
        sync_files: Whether to synchronize configuration
        **kwargs: Additional pandas read_csv parameters
        
    Returns:
        DataFrame containing CSV data
        
    Raises:
        FileNotFoundError: If file does not exist
        ValueError: If file is empty or contains no valid data
        RuntimeError: If file cannot be read with any supported encoding
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"CSV file not found: {file_path}")
        
    if os.path.getsize(file_path) == 0:
        raise ValueError(f"CSV file is empty: {file_path}")

    # Load CSV parameters from setup configuration
    config = _load_setup_config(sync_files)
    reader_config = _load_reader_config()
    csv_defaults_key = reader_config["csv_defaults_key"]
    csv_params = config[csv_defaults_key].copy()
    csv_params.update(kwargs)
    
    # Detect header row
    header_row = detect_csv_header_row(file_path)
    if header_row > 0:
        csv_params['skiprows'] = header_row

    # Detect separator if not provided
    if 'sep' not in kwargs:
        detected_sep = detect_csv_separator(file_path)
        if detected_sep:
            csv_params['sep'] = detected_sep
    
    # Try different encodings in order of preference
    encoding_priority = reader_config["encoding"]["csv_load_priority"]
    default_encoding = reader_config["encoding"]["default"] + "-sig"
    
    encodings_to_try = [
        csv_params.get('encoding', default_encoding),
    ] + encoding_priority
    
    last_error = None
    for encoding in encodings_to_try:
        try:
            csv_params['encoding'] = encoding
            df = pd.read_csv(file_path, **csv_params)
            
            # Handle single column case
            if df.shape[1] == 1 and csv_params['sep'] != ',':
                csv_params['sep'] = ','
                csv_params['decimal'] = '.'
                df = pd.read_csv(file_path, **csv_params)
            
            # Clean and validate data
            df = clean_dataframe_bom(df)
            df = df.dropna(how='all')
            df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
            
            if df.empty:
                raise ValueError("CSV file contains no valid data after cleaning")
            
            return df
            
        except UnicodeDecodeError as e:
            last_error = e
            continue
        except Exception as e:
            raise RuntimeError(f"Error loading CSV file {file_path}: {e}")
    
    raise RuntimeError(f"Could not decode CSV file {file_path} with any supported encoding. Last error: {last_error}")


def load_project_config(config_type: str, templates_folder: str) -> Dict[str, Any]:
    """Load specific project configuration file using cached loading.
    
    Args:
        config_type: Type of configuration to load
        templates_folder: Folder containing configuration files
        
    Returns:
        Dictionary containing project configuration data
        
    Raises:
        FileNotFoundError: If configuration file is not found
        RuntimeError: If configuration cannot be loaded
    """
    config_file = os.path.join(templates_folder, f"{config_type}.json")
    
    if not os.path.exists(config_file):
        raise FileNotFoundError(f"Configuration file not found: {config_file}")
        
    try:
        return _load_cached_files(config_file)
    except Exception as e:
        raise RuntimeError(f"Error loading {config_type} config from {config_file}: {e}")


def load_all_project_configs(templates_folder: str) -> Dict[str, Dict[str, Any]]:
    """Load all project configuration files using cached loading.
    
    Args:
        templates_folder: Folder containing configuration files
        
    Returns:
        Dictionary containing all project configuration data organized by type
        
    Raises:
        FileNotFoundError: If templates folder or required config files are not found
        RuntimeError: If configurations cannot be loaded
    """
    if not os.path.exists(templates_folder):
        raise FileNotFoundError(f"Templates folder not found: {templates_folder}")
    
    reader_config = _load_reader_config()
    config_types_filename = reader_config["file_paths"]["config_types_filename"]
    config_types_path = os.path.join(templates_folder, config_types_filename)
    
    if os.path.exists(config_types_path):
        try:
            config_data = _load_cached_files(config_types_path)
            default_config_types = reader_config["default_config_types"]
            configs = config_data.get('config_types', default_config_types)
        except Exception as e:
            raise RuntimeError(f"Error loading config types from {config_types_path}: {e}")
    else:
        configs = reader_config["default_config_types"]
    
    result = {}
    for config_type in configs:
        result[config_type] = load_project_config(config_type, templates_folder)
    
    return result


def find_csv_file(data_directory: str, filename: str) -> str:
    """Find CSV file in data directory with strict error handling.
    
    Args:
        data_directory: Directory containing CSV files
        filename: Name of the CSV file to find
        
    Returns:
        Full path to the CSV file
        
    Raises:
        FileNotFoundError: If file cannot be found
        ValueError: If data directory is invalid
    """
    if not data_directory:
        raise ValueError("Data directory path cannot be empty")
    
    if not os.path.exists(data_directory):
        raise FileNotFoundError(f"Data directory not found: {data_directory}")
    
    # Try exact filename first
    file_path = os.path.join(data_directory, filename)
    if os.path.exists(file_path):
        return file_path
    
    # Try with .csv extension if not present
    reader_config = _load_reader_config()
    csv_extension = reader_config["file_extensions"]["csv"]
    
    if not filename.endswith(csv_extension):
        file_path = os.path.join(data_directory, f"{filename}{csv_extension}")
        if os.path.exists(file_path):
            return file_path
    
    # Search recursively in subdirectories
    for root, _, files in os.walk(data_directory):
        for file in files:
            if file == filename or file == f"{filename}{csv_extension}":
                return os.path.join(root, file)
    
    raise FileNotFoundError(f"CSV file '{filename}' not found in data directory: {data_directory}")


def list_csv_files(data_directory: str) -> List[str]:
    """List all CSV files in data directory with strict error handling.
    
    Args:
        data_directory: Directory containing CSV files
        
    Returns:
        List of CSV file paths
        
    Raises:
        FileNotFoundError: If data directory does not exist
        ValueError: If data directory is invalid
    """
    if not data_directory:
        raise ValueError("Data directory path cannot be empty")
    
    if not os.path.exists(data_directory):
        raise FileNotFoundError(f"Data directory not found: {data_directory}")
    
    csv_files = []
    reader_config = _load_reader_config()
    csv_extension = reader_config["file_extensions"]["csv"]
    
    for root, _, files in os.walk(data_directory):
        for file in files:
            if file.lower().endswith(csv_extension):
                csv_files.append(os.path.join(root, file))
    
    return csv_files


def _get_file_path(base_dir: str, file_key: str, sync_files: bool = True) -> str:
    """Get full file path from setup configuration."""
    config = _load_setup_config(sync_files)
    reader_config = _load_reader_config()
    
    # Navigate through the nested structure to find the file
    files_key = reader_config["directory_keys"]["files"]
    files_config = config[files_key]
    
    def find_file_in_config(config_dict: Dict[str, Any], key: str) -> Optional[str]:
        """Recursively search for a file key in the nested configuration."""
        if isinstance(config_dict, dict):
            if key in config_dict and isinstance(config_dict[key], str):
                return config_dict[key]
            for value in config_dict.values():
                result = find_file_in_config(value, key)
                if result:
                    return result
        return None
    
    relative_path = find_file_in_config(files_config, file_key)
    if not relative_path:
        raise KeyError(f"File key '{file_key}' not found in setup configuration")
    
    # For data files, use data directory
    csv_suffix = reader_config["file_extensions"]["csv_suffix"]
    if file_key.endswith(csv_suffix):
        directories_key = reader_config["directory_keys"]["directories"]
        data_key = reader_config["directory_keys"]["data"]
        return os.path.join(base_dir, config[directories_key][data_key], relative_path)
    
    # For configuration files, use config directory
    directories_key = reader_config["directory_keys"]["directories"]
    config_key = reader_config["directory_keys"]["config"]
    return os.path.join(base_dir, config[directories_key][config_key], relative_path)


# LEGACY READFILES CLASS FOR BACKWARD COMPATIBILITY
class ReadFiles(BaseModel):
    """DEPRECATED: Legacy ReadFiles wrapper for backward compatibility.
    
    Use direct functions instead:
    - load_json_file(), load_text_file(), load_csv_file(), load_project_config()
    """

    file_path: str = Field(..., description="The path to the file")

    def _detect_header_row(self) -> int:
        return detect_csv_header_row(self.file_path)

    @staticmethod
    def clean_dataframe_bom(df: pd.DataFrame) -> pd.DataFrame:
        return clean_dataframe_bom(df)

    def load_json(self) -> Optional[Dict[str, Any]]:
        return load_json_file(self.file_path)
    
    def load_text(self) -> str:
        try:
            return load_text_file(self.file_path)
        except FileNotFoundError:
            return ""  # Legacy behavior for backward compatibility

    def _detect_separator(self) -> Optional[str]:
        return detect_csv_separator(self.file_path)

    def load_csv(self, sync_files: bool = True, **kwargs) -> pd.DataFrame:
        return load_csv_file(self.file_path, sync_files, **kwargs)

    @staticmethod
    def load_project_config(config_type: str, templates_folder: str) -> Dict[str, Any]:
        return load_project_config(config_type, templates_folder)
    
    @staticmethod
    def load_all_project_configs(templates_folder: str) -> Dict[str, Dict[str, Any]]:
        return load_all_project_configs(templates_folder)

    @staticmethod
    def find_csv_file(data_directory: str, filename: str) -> str:
        return find_csv_file(data_directory, filename)

    @staticmethod
    def list_csv_files(data_directory: str) -> List[str]:
        return list_csv_files(data_directory)



