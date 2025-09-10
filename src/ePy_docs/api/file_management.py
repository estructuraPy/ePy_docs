"""Portal to the files world - Clean API interface.

This module provides access to the files world containing the core file handling logic.
No business logic should exist here - only clean interfaces to the files world.
"""

from pathlib import Path
from typing import Dict, Any, Optional, Union
import pandas as pd

# Import the files world components
from ePy_docs.files.reader import ReadFiles
from ePy_docs.files.saver import SaveFiles

# Clean API functions - direct portals to files world
def read_csv(filepath: Union[str, Path], **kwargs) -> pd.DataFrame:
    """Portal to files world for CSV reading."""
    return ReadFiles(file_path=str(filepath)).load_csv(**kwargs)

def read_json(filepath: Union[str, Path]) -> Dict[str, Any]:
    """Portal to files world for JSON reading."""
    return ReadFiles(file_path=str(filepath)).load_json()

def read_text(filepath: Union[str, Path]) -> str:
    """Portal to files world for text reading."""
    return ReadFiles(file_path=str(filepath)).load_text()

def write_csv(data: pd.DataFrame, filepath: Union[str, Path], index: bool = False, **kwargs) -> None:
    """Portal to files world for CSV writing."""
    SaveFiles(file_path=str(filepath), auto_print=False).save_csv(data, index=index, **kwargs)

def write_json(data: Dict[str, Any], filepath: Union[str, Path], indent: int = 2) -> None:
    """Portal to files world for JSON writing."""
    SaveFiles(file_path=str(filepath), auto_print=False).save_json(data, indent=indent)

def write_text(content: str, filepath: Union[str, Path]) -> None:
    """Portal to files world for text writing."""
    SaveFiles(file_path=str(filepath), auto_print=False).save_txt(content)
