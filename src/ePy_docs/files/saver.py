"""
Pure file saving utilities for ePy_docs FILES world.

Direct file operations without class overhead or verbose contamination.
TRANSPARENCY DIMENSION: Silent operations, no fallbacks, no wrappers.
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Union

import matplotlib.pyplot as plt
import pandas as pd


def ensure_directory(file_path: str) -> None:
    """Ensure the directory for the file path exists.
    
    Args:
        file_path: Path to file whose directory should be created
    """
    Path(file_path).parent.mkdir(parents=True, exist_ok=True)


def save_json(file_path: str, data: Dict[str, Any], indent: int = 2) -> None:
    """Save data as JSON file with pure operations.
    
    Args:
        file_path: Path where to save the JSON file
        data: Dictionary data to save as JSON
        indent: Number of spaces for JSON indentation
        
    Raises:
        TypeError: If data is not JSON serializable
        OSError: If file cannot be written
    """
    ensure_directory(file_path)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=indent)


def save_csv(file_path: str, data: Union[List[List], pd.DataFrame], 
             delimiter: str = ',', index: bool = False) -> None:
    """Save data as CSV file using pure pandas operations.
    
    Args:
        file_path: Path where to save the CSV file
        data: DataFrame or list of lists containing CSV data
        delimiter: Character to separate CSV fields
        index: Whether to include DataFrame index (only for DataFrames)
        
    Raises:
        ValueError: If data format is invalid
        OSError: If file cannot be written
    """
    ensure_directory(file_path)
    
    if isinstance(data, pd.DataFrame):
        # Pure pandas operation - no wrapper contamination
        data.to_csv(file_path, sep=delimiter, index=index, encoding='utf-8')
    elif isinstance(data, list):
        # Direct file writing for list of lists
        with open(file_path, 'w', encoding='utf-8') as f:
            for row in data:
                f.write(delimiter.join([str(cell) for cell in row]) + '\n')
    else:
        raise ValueError("data must be pandas DataFrame or list of lists")


def save_txt(file_path: str, content: str) -> None:
    """Save text content to file with pure operations.
    
    Args:
        file_path: Path where to save the text file
        content: Text content to save
        
    Raises:
        OSError: If file cannot be written
    """
    ensure_directory(file_path)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)


def save_excel(file_path: str, dataframe: Union[pd.DataFrame, Dict[str, pd.DataFrame]], 
               decimal_separator: str = '.', sheet_name: str = 'Sheet1',
               index: bool = True, header: bool = True) -> None:
    """Save DataFrame(s) to Excel file using pure pandas operations.
    
    Args:
        file_path: Path where to save the Excel file
        dataframe: Single DataFrame or dictionary of DataFrames {sheet_name: DataFrame}
        decimal_separator: Decimal separator for numeric values ('.' or ',')
        sheet_name: Default sheet name when saving single DataFrame
        index: Whether to include row index in output
        header: Whether to include column headers in output
        
    Raises:
        ValueError: If dataframe format is invalid
        OSError: If file cannot be written
    """
    ensure_directory(file_path)
    
    # Prepare data based on input type
    if isinstance(dataframe, pd.DataFrame):
        data_dict = {sheet_name: dataframe}
    elif isinstance(dataframe, dict):
        data_dict = dataframe
    else:
        raise ValueError("dataframe must be a pandas DataFrame or dictionary of DataFrames")
    
    # Handle decimal separator if different from default
    if decimal_separator == ',':
        formatted_data = {}
        for name, df in data_dict.items():
            df_copy = df.copy()
            # Convert numeric columns to string with comma separator
            for col in df_copy.select_dtypes(include=['float64', 'float32', 'int64', 'int32']).columns:
                df_copy[col] = df_copy[col].astype(str).str.replace('.', ',', regex=False)
            formatted_data[name] = df_copy
        data_dict = formatted_data
    
    # Pure pandas Excel writing - no verbose contamination
    with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
        for name, df in data_dict.items():
            df.to_excel(writer, sheet_name=name, index=index, header=header)


def save_matplotlib_figure(fig: plt.Figure, filename: str, 
                           format: str = 'png', dpi: int = 300, 
                           bbox_inches: str = 'tight', 
                           directory: Optional[str] = None,
                           create_dir: bool = True) -> str:
    """Save matplotlib figure to file with pure operations.
    
    Args:
        fig: The matplotlib figure to save
        filename: Base filename without extension
        format: File format ('png', 'pdf', 'svg', 'jpg', etc.)
        dpi: Resolution for raster formats
        bbox_inches: Bounding box setting
        directory: Target directory, uses current directory if None
        create_dir: Whether to create directory if it doesn't exist
        
    Returns:
        Full path to saved file
        
    Raises:
        OSError: If file cannot be written
    """
    if directory is None:
        directory = os.getcwd()
    
    if create_dir:
        os.makedirs(directory, exist_ok=True)
    
    clean_filename = filename.replace(' ', '_').replace('/', '_').replace('\\', '_')
    if not clean_filename.endswith(f'.{format}'):
        clean_filename = f"{clean_filename}.{format}"
    
    filepath = os.path.join(directory, clean_filename)
    
    save_kwargs = {
        'format': format,
        'bbox_inches': bbox_inches,
        'facecolor': 'white',
        'edgecolor': 'none'
    }
    
    if format.lower() in ['png', 'jpg', 'jpeg', 'tiff']:
        save_kwargs['dpi'] = dpi
    
    # Silent operation - no verbose contamination
    fig.savefig(filepath, **save_kwargs)
    return filepath


# Legacy SaveFiles class for backward compatibility during transition
class SaveFiles:
    """DEPRECATED: Legacy SaveFiles wrapper for backward compatibility.
    
    Use direct functions instead:
    - save_json(), save_csv(), save_txt(), save_excel(), save_matplotlib_figure()
    """
    
    def __init__(self, file_path: str, auto_print: bool = False, content_buffer: List[str] = None):
        self.file_path = file_path
        self.auto_print = auto_print  # Ignored - no verbose operations
        self.content_buffer = content_buffer or []
        ensure_directory(file_path)
    
    def save_json(self, data: Dict[str, Any], indent: int) -> None:
        save_json(self.file_path, data, indent)
    
    def save_csv(self, data: Union[List[List], pd.DataFrame], delimiter: str = ',', index: bool = False) -> None:
        save_csv(self.file_path, data, delimiter, index)
    
    def save_txt(self, content: str) -> None:
        save_txt(self.file_path, content)
    
    def save_excel(self, dataframe: Union[pd.DataFrame, Dict[str, pd.DataFrame]], 
                   decimal_separator: str = '.', sheet_name: str = 'Sheet1',
                   index: bool = True, header: bool = True) -> None:
        save_excel(self.file_path, dataframe, decimal_separator, sheet_name, index, header)
    
    def save_matplotlib_figure(self, fig: plt.Figure, filename: str, 
                               format: str = 'png', dpi: int = 300, 
                               bbox_inches: str = 'tight', 
                               directory: Optional[str] = None,
                               create_dir: bool = True) -> str:
        if directory is None:
            directory = os.path.dirname(self.file_path) or os.getcwd()
        return save_matplotlib_figure(fig, filename, format, dpi, bbox_inches, directory, create_dir)

