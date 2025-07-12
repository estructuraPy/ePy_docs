"""Image processing and management for reports and presentations.

Provides shared image handling capabilities including optimization,
format conversion, and display management.
"""

import os
import shutil
from typing import Optional


class ImageProcessor:
    """Processor for image handling across different output formats."""
    
    @staticmethod
    def organize_image(path: str, output_dir: str, image_type: str = "figures") -> str:
        """Organize image into appropriate subdirectory.
        
        Args:
            path: Source image path
            output_dir: Base output directory
            image_type: Type of image (figures, tables, notes, etc.)
            
        Returns:
            Organized image path
        """
        # Determine subdirectory based on image type or path
        if image_type == "auto":
            if 'table' in path.lower():
                subdir = "tables"
            elif 'note' in path.lower():
                subdir = "notes"
            else:
                subdir = "figures"
        else:
            subdir = image_type
        
        # Create destination directory
        dest_dir = os.path.join(output_dir, subdir)
        os.makedirs(dest_dir, exist_ok=True)
        dest_path = os.path.join(dest_dir, os.path.basename(path))
        
        # Copy the file if needed
        if path != dest_path:
            shutil.copy2(path, dest_path)
        
        return dest_path
    
    @staticmethod
    def get_relative_path(img_path: str, output_dir: str) -> str:
        """Get relative path for cross-platform compatibility.
        
        Args:
            img_path: Absolute image path
            output_dir: Base output directory
            
        Returns:
            Relative path with forward slashes
        """
        return os.path.relpath(img_path, output_dir).replace('\\', '/')
    
    @staticmethod
    def validate_image_format(path: str, allowed_formats: list = None) -> bool:
        """Validate image format.
        
        Args:
            path: Image file path
            allowed_formats: List of allowed extensions
            
        Returns:
            True if format is valid
        """
        if allowed_formats is None:
            allowed_formats = ['.png', '.jpg', '.jpeg', '.svg', '.pdf']
        
        _, ext = os.path.splitext(path.lower())
        return ext in allowed_formats
