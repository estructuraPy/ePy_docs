import os
import json
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

import matplotlib.pyplot as plt

class SaveFiles(BaseModel):
    """Base class for writing files with comprehensive format support.
    
    Assumptions:
        File paths are valid and accessible for writing operations
        Required directories can be created if they don't exist
        File system permissions allow file creation and modification
    """
    file_path: str
    content_buffer: List[str] = Field(default_factory=list)
    auto_print: bool = Field(description="Whether to print content to console")

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

    def save_csv(self, data: List[List], delimiter: str) -> None:
        """Save data as CSV file.
        
        Args:
            data: List of lists containing CSV data
            delimiter: Character to separate CSV fields
            
        Assumptions:
            Data can be converted to string format
            File path is writable and directory exists
        """
        with open(self.file_path, 'w', encoding='utf-8') as f:
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

