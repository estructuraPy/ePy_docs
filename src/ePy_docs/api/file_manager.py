"""Portal to the files world - Clean API interface.

This module provides access to the files world containing the core file handling logic.
No business logic should exist here - only clean interfaces to the files world.
TRANSPARENCY DIMENSION: Pure functions, no class overhead, silent operations.
"""

from pathlib import Path
from typing import Dict, Any, Optional, Union
import pandas as pd

# Import pure functions from files world
from ePy_docs.files.reader import (
    load_csv_file, load_json_file, load_text_file, ReadFiles  # ReadFiles for legacy compatibility
)
from ePy_docs.files.saver import (
    save_csv, save_json, save_txt, save_excel, save_matplotlib_figure,
    ensure_directory
)

# Clean API functions - direct portals to files world
def read_csv(filepath: Union[str, Path], **kwargs) -> pd.DataFrame:
    """Portal to files world for CSV reading using pure functions."""
    return load_csv_file(str(filepath), **kwargs)

def read_json(filepath: Union[str, Path]) -> Dict[str, Any]:
    """Portal to files world for JSON reading using pure functions."""
    return load_json_file(str(filepath))

def read_text(filepath: Union[str, Path]) -> str:
    """Portal to files world for text reading using pure functions."""
    return load_text_file(str(filepath))

def write_csv(data: pd.DataFrame, filepath: Union[str, Path], index: bool = False, 
              delimiter: str = ',', **kwargs) -> None:
    """Portal to files world for CSV writing using pure functions."""
    save_csv(str(filepath), data, delimiter=delimiter, index=index)

def write_json(data: Dict[str, Any], filepath: Union[str, Path], indent: int = 2) -> None:
    """Portal to files world for JSON writing using pure functions."""
    save_json(str(filepath), data, indent=indent)

def write_text(content: str, filepath: Union[str, Path]) -> None:
    """Portal to files world for text writing using pure functions."""
    save_txt(str(filepath), content)

def write_excel(data: Union[pd.DataFrame, Dict[str, pd.DataFrame]], 
                filepath: Union[str, Path], decimal_separator: str = '.', 
                sheet_name: str = 'Sheet1', index: bool = True, 
                header: bool = True) -> None:
    """Portal to files world for Excel writing using pure functions."""
    save_excel(str(filepath), data, decimal_separator, sheet_name, index, header)

def create_directory(directory_path: Union[str, Path]) -> None:
    """Portal to files world for directory creation using pure functions."""
    ensure_directory(str(directory_path))
