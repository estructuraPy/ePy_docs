"""File reading utilities for different formats with robust error handling.

Provides comprehensive file reading capabilities for CSV, JSON, and configuration files
with automatic encoding detection and format validation.
"""

import os
import re
import json
from typing import List, Any, Dict, Optional
from functools import lru_cache
from pathlib import Path

import pandas as pd
from pydantic import BaseModel, Field

from ePy_docs.files.data import _load_cached_json


@lru_cache(maxsize=1)
def _load_reader_config() -> Dict[str, Any]:
    """Load reader configuration from JSON file."""
    config_path = Path(__file__).parent / "reader.json"
    if not config_path.exists():
        raise FileNotFoundError(f"Reader configuration file not found: {config_path}")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def _load_setup_config(sync_json: bool = True) -> Dict[str, Any]:
    """Load configuration from setup.json file using the project configuration manager.
    
    Args:
        sync_json: Whether to synchronize from source before loading.
        
    Returns:
        Dictionary containing setup configuration data.
        
    Raises:
        RuntimeError: If setup configuration cannot be loaded.
    """
    from ePy_docs.core.setup import load_setup_config
    return load_setup_config(sync_json)


def _get_file_path(base_dir: str, file_key: str, sync_json: bool = True) -> str:
    """Get full file path from setup configuration."""
    config = _load_setup_config(sync_json)
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



class ReadFiles(BaseModel):
    """Class to read files of different formats with comprehensive error handling.

    Provides methods for reading CSV, JSON, and configuration files with automatic
    format detection, encoding handling, and data cleaning capabilities.
    
    Assumptions:
        File paths are valid and accessible
        Input files follow standard format conventions
        Required permissions are available for file access
    """

    file_path: str = Field(..., description="The path to the file")

    def _detect_header_row(self) -> int:
        """Detect the header row in CSV files by looking for numeric patterns.
        
        Returns:
            Row number containing the header (0-based index).
        """
        reader_config = _load_reader_config()
        encodings_to_try = reader_config["encoding"]["header_detection"]
        sample_rows = reader_config["csv_detection"]["sample_rows"]
        default_separator = reader_config["csv_detection"]["default_separator"]
        text_threshold = reader_config["csv_detection"]["text_threshold"]
        
        for encoding in encodings_to_try:
            try:
                # Try to detect header row by reading first few rows
                sample_df = pd.read_csv(self.file_path, sep=default_separator, nrows=sample_rows, header=None, encoding=encoding)
                
                for idx, row in sample_df.iterrows():
                    # Check if row contains mostly text (likely header)
                    text_count = sum(1 for val in row if isinstance(val, str) and not str(val).replace('.', '').replace(',', '').replace('-', '').isdigit())
                    if text_count > len(row) * text_threshold:  # More than configured threshold text
                        return idx
                return 0
            except (UnicodeDecodeError, pd.errors.EmptyDataError):
                continue
            except Exception:
                return 0
        
        return 0

    @staticmethod
    def clean_dataframe_bom(df: pd.DataFrame) -> pd.DataFrame:
        """Remove BOM (Byte Order Mark) from all column names in the DataFrame.
        
        Args:
            df: DataFrame with potentially BOM-affected column names.
            
        Returns:
            DataFrame with cleaned column names.
            
        Assumptions:
            DataFrame has at least one column.
            BOM characters can appear at the beginning of any column name.
        """
        if df.empty:
            return df
            
        # Remove BOM characters from all column names
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

    def load_json(self) -> Optional[Dict[str, Any]]:
        """Load JSON file with strict error handling.
        
        Returns:
            Dictionary if successful, None if failed.
        """
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"JSON file not found: {self.file_path}")
            
        if os.path.getsize(self.file_path) == 0:
            raise ValueError(f"JSON file is empty: {self.file_path}")
        
        try:
            return _load_cached_json(self.file_path)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format in {self.file_path}: {e}")
        except Exception as e:
            raise RuntimeError(f"Error reading JSON {self.file_path}: {e}")
    
    def _detect_separator(self) -> Optional[str]:
        """Detect CSV separator by analyzing file content with encoding detection.
        
        Returns:
            Most likely separator or None if detection fails.
        """
        reader_config = _load_reader_config()
        encodings_to_try = reader_config["encoding"]["separator_detection"]
        sample_lines_count = reader_config["csv_detection"]["sample_lines_separator"]
        
        for encoding in encodings_to_try:
            try:
                with open(self.file_path, 'r', encoding=encoding) as f:
                    sample_lines = f.readlines()[:sample_lines_count]
                break
            except UnicodeDecodeError:
                continue
        else:
            # If all encodings fail, return None
            return None
        
        if not sample_lines:
            return None
        
        separators = reader_config["csv_detection"]["separators"]
        separator_scores = {}
        
        for sep in separators:
            separator_scores[sep] = sum(line.count(sep) for line in sample_lines)
        
        if separator_scores:
            detected_sep = max(separator_scores, key=separator_scores.get)
            if separator_scores[detected_sep] > 0:
                return detected_sep
        
        return None

    def load_csv(self, sync_json: bool = True, **kwargs) -> pd.DataFrame:
        """Load CSV file with configuration-based parameters and robust encoding detection."""
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"CSV file not found: {self.file_path}")
            
        if os.path.getsize(self.file_path) == 0:
            raise ValueError(f"CSV file is empty: {self.file_path}")

        # Load CSV parameters from setup configuration
        config = _load_setup_config(sync_json)
        reader_config = _load_reader_config()
        csv_defaults_key = reader_config["csv_defaults_key"]
        csv_params = config[csv_defaults_key].copy()
        csv_params.update(kwargs)
        
        # Detect header row
        header_row = self._detect_header_row()
        if header_row > 0:
            csv_params['skiprows'] = header_row

        # Detect separator if not provided
        if 'sep' not in kwargs:
            detected_sep = self._detect_separator()
            if detected_sep:
                csv_params['sep'] = detected_sep
        
        # Try different encodings in order of preference
        encoding_priority = reader_config["encoding"]["csv_load_priority"]
        default_encoding = reader_config["encoding"]["default"] + "-sig"
        
        encodings_to_try = [
            csv_params.get('encoding', default_encoding),  # From config first
        ] + encoding_priority
        
        last_error = None
        for encoding in encodings_to_try:
            try:
                csv_params['encoding'] = encoding
                df = pd.read_csv(self.file_path, **csv_params)
                
                # Handle single column case
                if df.shape[1] == 1 and csv_params['sep'] != ',':
                    csv_params['sep'] = ','
                    csv_params['decimal'] = '.'
                    df = pd.read_csv(self.file_path, **csv_params)
                
                # Clean and validate data
                df = self.clean_dataframe_bom(df)
                df = df.dropna(how='all')
                df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
                
                if df.empty:
                    raise ValueError("CSV file contains no valid data after cleaning")
                
                return df
                
            except UnicodeDecodeError as e:
                last_error = e
                continue
            except Exception as e:
                # If it's not an encoding error, raise immediately
                raise RuntimeError(f"Error loading CSV file {self.file_path}: {e}")
        
        # If all encodings failed, raise the last encoding error
        raise RuntimeError(f"Could not decode CSV file {self.file_path} with any supported encoding. Last error: {last_error}")

    @staticmethod
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
            
        Assumptions:
            Configuration files follow the naming pattern {config_type}.json
            Templates folder structure is properly organized
        """
        config_file = os.path.join(templates_folder, f"{config_type}.json")
        
        if not os.path.exists(config_file):
            raise FileNotFoundError(f"Configuration file not found: {config_file}")
            
        try:
            return _load_cached_json(config_file)
        except Exception as e:
            raise RuntimeError(f"Error loading {config_type} config from {config_file}: {e}")
    
    @staticmethod
    def load_all_project_configs(templates_folder: str) -> Dict[str, Dict[str, Any]]:
        """Load all project configuration files using cached loading.
        
        Args:
            templates_folder: Folder containing configuration files
            
        Returns:
            Dictionary containing all project configuration data organized by type
            
        Raises:
            FileNotFoundError: If templates folder or required config files are not found
            RuntimeError: If configurations cannot be loaded
            
        Assumptions:
            Standard configuration files exist in the templates folder
            Configuration types follow expected naming conventions
        """
        if not os.path.exists(templates_folder):
            raise FileNotFoundError(f"Templates folder not found: {templates_folder}")
        
        # Load configuration types from config file or use defaults
        reader_config = _load_reader_config()
        config_types_filename = reader_config["file_paths"]["config_types_filename"]
        config_types_path = os.path.join(templates_folder, config_types_filename)
        
        if os.path.exists(config_types_path):
            try:
                config_data = _load_cached_json(config_types_path)
                default_config_types = reader_config["default_config_types"]
                configs = config_data.get('config_types', default_config_types)
            except Exception as e:
                raise RuntimeError(f"Error loading config types from {config_types_path}: {e}")
        else:
            # Use default configuration types
            configs = reader_config["default_config_types"]
        
        result = {}
        
        for config_type in configs:
            result[config_type] = ReadFiles.load_project_config(config_type, templates_folder)
        
        return result

    @staticmethod
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

    @staticmethod
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



