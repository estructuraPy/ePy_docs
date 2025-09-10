import os
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field

import matplotlib.pyplot as plt
import pandas as pd

class SaveFiles(BaseModel):
    """Core file saving logic in the files world.
    
    Handles all file writing operations with automatic directory creation
    and comprehensive format support.
    """
    file_path: str
    content_buffer: List[str] = Field(default_factory=list)
    auto_print: bool = Field(description="Whether to print content to console")

    def model_post_init(self, __context):
        """Ensure directory exists when SaveFiles is created."""
        self._ensure_directory()

    def _ensure_directory(self) -> None:
        """Ensure the directory for the file path exists."""
        Path(self.file_path).parent.mkdir(parents=True, exist_ok=True)

    def save_json(self, data: Dict[str, Any], indent: int) -> None:
        """Save data as JSON file.
        
        Args:
            data: Dictionary data to save as JSON
            indent: Number of spaces for JSON indentation
            
        Assumptions:
            Data is JSON serializable
            File path is writable and directory exists
        """
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=indent)

    def save_csv(self, data: Union[List[List], pd.DataFrame], delimiter: str = ',', index: bool = False) -> None:
        """Save data as CSV file.
        
        Args:
            data: List of lists or DataFrame containing CSV data
            delimiter: Character to separate CSV fields
            index: Whether to include DataFrame index (only for DataFrames)
            
        Assumptions:
            Data can be converted to string format
            File path is writable and directory exists
        """
        with open(self.file_path, 'w', encoding='utf-8') as f:
            if isinstance(data, pd.DataFrame):
                # Convert DataFrame to list of lists
                data_list = []
                
                # Add headers
                if index:
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
                
                data = data_list
            
            # Write list of lists
            for row in data:
                f.write(delimiter.join([str(cell) for cell in row]) + '\n')

    def save_txt(self, content: str) -> None:
        """Save text content to file.
        
        Args:
            content: Text content to save.
            
        Assumptions:
            Content is properly encoded string.
            File path is writable and directory exists.
        """
        with open(self.file_path, 'w', encoding='utf-8') as f:
            f.write(content)

    def save_excel(self, dataframe: Union[pd.DataFrame, Dict[str, pd.DataFrame]], 
                   decimal_separator: str = '.', 
                   sheet_name: str = 'Sheet1',
                   index: bool = True,
                   header: bool = True) -> None:
        """Save DataFrame(s) to Excel file with configurable decimal separator.
        
        Args:
            dataframe: Single DataFrame or dictionary of DataFrames {sheet_name: DataFrame}
            decimal_separator: Decimal separator for numeric values ('.' or ',')
            sheet_name: Default sheet name when saving single DataFrame
            index: Whether to include row index in output
            header: Whether to include column headers in output
            
        Assumptions:
            DataFrame contains valid data that can be exported to Excel
            File path has .xlsx extension and directory is writable
            Excel engine (openpyxl) is available
        """
        try:
            # Prepare data based on input type
            if isinstance(dataframe, pd.DataFrame):
                # Single DataFrame
                data_dict = {sheet_name: dataframe}
            elif isinstance(dataframe, dict):
                # Multiple DataFrames
                data_dict = dataframe
            else:
                raise ValueError("dataframe must be a pandas DataFrame or dictionary of DataFrames")
            
            # Handle decimal separator if different from default
            if decimal_separator == ',':
                # Create copies of DataFrames with modified numeric formatting
                formatted_data = {}
                for name, df in data_dict.items():
                    df_copy = df.copy()
                    # Convert numeric columns to string with comma separator
                    for col in df_copy.select_dtypes(include=['float64', 'float32', 'int64', 'int32']).columns:
                        df_copy[col] = df_copy[col].astype(str).str.replace('.', ',', regex=False)
                    formatted_data[name] = df_copy
                data_dict = formatted_data
            
            # Save to Excel
            with pd.ExcelWriter(self.file_path, engine='openpyxl') as writer:
                for name, df in data_dict.items():
                    df.to_excel(writer, sheet_name=name, index=index, header=header)
            
            if self.auto_print:
                print(f"Excel file saved: {self.file_path}")
                if len(data_dict) > 1:
                    print(f"Sheets: {list(data_dict.keys())}")
                    
        except Exception as e:
            if self.auto_print:
                print(f"Error saving Excel file: {e}")
            raise

    def save_matplotlib_figure(self, fig: plt.Figure, filename: str, 
                   format: str = 'png', dpi: int = 300, 
                   bbox_inches: str = 'tight', 
                   directory: Optional[str] = None,
                   create_dir: bool = True) -> str:
        """Save a matplotlib figure to file with proper path handling.
        
        Args:
            fig: The matplotlib figure to save
            filename: Base filename without extension
            format: File format ('png', 'pdf', 'svg', 'jpg', etc.)
            dpi: Resolution for raster formats
            bbox_inches: Bounding box setting
            directory: Target directory, uses file_path directory if None
            create_dir: Whether to create directory if it doesn't exist
            
        Returns:
            Full path to saved file
            
        Assumptions:
            matplotlib figure is valid and accessible
            File system permissions allow file creation and directory creation
        """
        try:
            if directory is None:
                directory = os.path.dirname(self.file_path) or os.getcwd()
            
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
            
            fig.savefig(filepath, **save_kwargs)
            
            if self.auto_print:
                print(f"Figure saved: {filepath}")
            return filepath
            
        except Exception as e:
            if self.auto_print:
                print(f"Error saving figure: {e}")
            return ""

