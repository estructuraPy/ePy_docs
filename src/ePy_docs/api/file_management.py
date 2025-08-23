"""Simple and direct file management API for ePy_docs.

This module provides a straightforward interface for reading and writing multiple file types,
using the specialized modules from the files package. Designed for simplicity with minimal parameters.
"""

import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Union

import pandas as pd

from ePy_docs.files.reader import ReadFiles
from ePy_docs.files.saver import SaveFiles


class FileManager:
    """Simple file manager with direct read/write operations for multiple file types.
    
    Features:
    - Read/write CSV, JSON, TXT files using specialized files modules
    - Automatic directory creation
    - Simple parameter interface
    - Built on existing files infrastructure
    """
    
    def __init__(self, base_dir: Optional[str] = None):
        """Initialize file manager.
        
        Args:
            base_dir: Optional base directory for relative paths
        """
        self.base_dir = Path(base_dir) if base_dir else Path.cwd()
    
    def _get_full_path(self, filepath: Union[str, Path]) -> Path:
        """Get full path, resolving relative paths against base_dir."""
        path = Path(filepath)
        if not path.is_absolute():
            path = self.base_dir / path
        return path
    
    def _ensure_directory(self, filepath: Path) -> None:
        """Ensure the directory for the filepath exists."""
        filepath.parent.mkdir(parents=True, exist_ok=True)
    
    # =====================
    # READ OPERATIONS
    # =====================
    
    def read_csv(self, filepath: Union[str, Path]) -> pd.DataFrame:
        """Read CSV file using ReadFiles module.
        
        Args:
            filepath: Path to CSV file
            
        Returns:
            DataFrame with the CSV content
        """
        full_path = self._get_full_path(filepath)
        if not full_path.exists():
            raise FileNotFoundError(f"CSV file not found: {full_path}")
        
        reader = ReadFiles(file_path=str(full_path))
        return reader.load_csv()
    
    def read_json(self, filepath: Union[str, Path]) -> Dict[str, Any]:
        """Read JSON file using ReadFiles module.
        
        Args:
            filepath: Path to JSON file
            
        Returns:
            Dictionary with JSON content
        """
        full_path = self._get_full_path(filepath)
        if not full_path.exists():
            raise FileNotFoundError(f"JSON file not found: {full_path}")
        
        reader = ReadFiles(file_path=str(full_path))
        return reader.load_json()
    
    def read_text(self, filepath: Union[str, Path]) -> str:
        """Read text file directly (ReadFiles doesn't have text method).
        
        Args:
            filepath: Path to text file
            
        Returns:
            String with file content
        """
        full_path = self._get_full_path(filepath)
        if not full_path.exists():
            raise FileNotFoundError(f"Text file not found: {full_path}")
        
        with open(full_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def read_multiple(self, filepaths: List[Union[str, Path]]) -> Dict[str, Any]:
        """Read multiple files of different types.
        
        Args:
            filepaths: List of file paths to read
            
        Returns:
            Dictionary with filename as key and content as value
        """
        results = {}
        
        for filepath in filepaths:
            full_path = self._get_full_path(filepath)
            filename = full_path.name
            
            try:
                if full_path.suffix.lower() == '.csv':
                    results[filename] = self.read_csv(full_path)
                elif full_path.suffix.lower() == '.json':
                    results[filename] = self.read_json(full_path)
                else:
                    results[filename] = self.read_text(full_path)
            except Exception as e:
                results[filename] = f"Error reading file: {str(e)}"
        
        return results
    
    # =====================
    # WRITE OPERATIONS
    # =====================
    
    def write_csv(self, data: pd.DataFrame, filepath: Union[str, Path], index: bool = False) -> None:
        """Write DataFrame to CSV file using SaveFiles module.
        
        Args:
            data: DataFrame to write
            filepath: Path for output CSV file
            index: Whether to include DataFrame index in CSV
        """
        full_path = self._get_full_path(filepath)
        self._ensure_directory(full_path)
        
        saver = SaveFiles(file_path=str(full_path), auto_print=False)
        
        # Convert DataFrame to list of lists for SaveFiles.save_csv
        data_list = []
        if index:
            # Include column headers with index name if provided
            headers = [data.index.name or 'index'] + data.columns.tolist()
        else:
            headers = data.columns.tolist()
        data_list.append(headers)
        
        # Add data rows
        for idx, row in data.iterrows():
            if index:
                row_data = [str(idx)] + [str(val) for val in row.values]
            else:
                row_data = [str(val) for val in row.values]
            data_list.append(row_data)
        
        saver.save_csv(data_list, delimiter=',')
    
    def write_json(self, data: Dict[str, Any], filepath: Union[str, Path], indent: int = 2) -> None:
        """Write dictionary to JSON file using SaveFiles module.
        
        Args:
            data: Dictionary to write as JSON
            filepath: Path for output JSON file
            indent: JSON indentation (spaces)
        """
        full_path = self._get_full_path(filepath)
        self._ensure_directory(full_path)
        
        saver = SaveFiles(file_path=str(full_path), auto_print=False)
        saver.save_json(data, indent=indent)
    
    def write_text(self, content: str, filepath: Union[str, Path]) -> None:
        """Write text content to file using SaveFiles module.
        
        Args:
            content: Text content to write
            filepath: Path for output text file
        """
        full_path = self._get_full_path(filepath)
        self._ensure_directory(full_path)
        
        saver = SaveFiles(file_path=str(full_path), auto_print=False)
        saver.save_txt(content)
    
    def write_multiple(self, data_dict: Dict[str, Any], base_path: Optional[Union[str, Path]] = None) -> None:
        """Write multiple data objects to files based on their type.
        
        Args:
            data_dict: Dictionary with filename as key and data as value
            base_path: Optional base path for all files
        """
        if base_path:
            base_path = self._get_full_path(base_path)
        else:
            base_path = self.base_dir
        
        for filename, data in data_dict.items():
            filepath = base_path / filename
            
            try:
                if isinstance(data, pd.DataFrame):
                    # Ensure CSV extension
                    if not filepath.suffix:
                        filepath = filepath.with_suffix('.csv')
                    self.write_csv(data, filepath)
                
                elif isinstance(data, dict):
                    # Ensure JSON extension
                    if not filepath.suffix:
                        filepath = filepath.with_suffix('.json')
                    self.write_json(data, filepath)
                
                elif isinstance(data, str):
                    # Default to TXT extension if none
                    if not filepath.suffix:
                        filepath = filepath.with_suffix('.txt')
                    self.write_text(data, filepath)
                
                else:
                    # Convert to JSON for other types
                    if not filepath.suffix:
                        filepath = filepath.with_suffix('.json')
                    self.write_json({'data': str(data)}, filepath)
                    
            except Exception as e:
                raise RuntimeError(f"Error writing {filename}: {str(e)}")
    
    # =====================
    # UTILITY OPERATIONS
    # =====================
    
    def exists(self, filepath: Union[str, Path]) -> bool:
        """Check if file exists.
        
        Args:
            filepath: Path to check
            
        Returns:
            True if file exists, False otherwise
        """
        return self._get_full_path(filepath).exists()
    
    def list_files(self, directory: Optional[Union[str, Path]] = None, pattern: str = "*") -> List[Path]:
        """List files in directory matching pattern.
        
        Args:
            directory: Directory to list (uses base_dir if None)
            pattern: File pattern to match (e.g., "*.csv", "*.json")
            
        Returns:
            List of Path objects matching the pattern
        """
        if directory:
            dir_path = self._get_full_path(directory)
        else:
            dir_path = self.base_dir
        
        if not dir_path.exists():
            return []
        
        return list(dir_path.glob(pattern))
    
    def copy_file(self, source: Union[str, Path], destination: Union[str, Path]) -> None:
        """Copy file from source to destination.
        
        Args:
            source: Source file path
            destination: Destination file path
        """
        import shutil
        
        source_path = self._get_full_path(source)
        dest_path = self._get_full_path(destination)
        
        if not source_path.exists():
            raise FileNotFoundError(f"Source file not found: {source_path}")
        
        self._ensure_directory(dest_path)
        shutil.copy2(source_path, dest_path)


# =====================
# CONVENIENCE FUNCTIONS
# =====================

def read_csv(filepath: Union[str, Path], base_dir: Optional[str] = None) -> pd.DataFrame:
    """Quick function to read a CSV file."""
    fm = FileManager(base_dir)
    return fm.read_csv(filepath)

def read_json(filepath: Union[str, Path], base_dir: Optional[str] = None) -> Dict[str, Any]:
    """Quick function to read a JSON file."""
    fm = FileManager(base_dir)
    return fm.read_json(filepath)

def read_text(filepath: Union[str, Path], base_dir: Optional[str] = None) -> str:
    """Quick function to read a text file."""
    fm = FileManager(base_dir)
    return fm.read_text(filepath)

def write_csv(data: pd.DataFrame, filepath: Union[str, Path], base_dir: Optional[str] = None, index: bool = False) -> None:
    """Quick function to write a CSV file."""
    fm = FileManager(base_dir)
    fm.write_csv(data, filepath, index)

def write_json(data: Dict[str, Any], filepath: Union[str, Path], base_dir: Optional[str] = None, indent: int = 2) -> None:
    """Quick function to write a JSON file."""
    fm = FileManager(base_dir)
    fm.write_json(data, filepath, indent)

def write_text(content: str, filepath: Union[str, Path], base_dir: Optional[str] = None) -> None:
    """Quick function to write a text file."""
    fm = FileManager(base_dir)
    fm.write_text(content, filepath)
