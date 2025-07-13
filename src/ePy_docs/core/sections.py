import os
from typing import Optional
from pydantic import BaseModel

from ePy_docs.files.data import _load_cached_json

class WatermarkConfig(BaseModel):
    """Configuration for watermark settings.
    
    Assumptions:
        All configuration values are loaded from JSON files
        Watermark files exist in expected locations or are properly configured
    """
    watermark_path: Optional[str]
    opacity: float
    position: str
    scale: float
    enabled: bool
    
    @property
    def default_watermark_path(self) -> str:
        """Gets the default watermark path relative to current working directory.
        
        Returns:
            Default path to watermark image file
            
        Assumptions:
            Brand directory follows standard project structure
        """
        return os.path.join(os.getcwd(), "brand", "watermark.png")
    
    def get_watermark_path(self) -> Optional[str]:
        """Gets the actual watermark path, checking if file exists.
        
        Returns:
            Path to existing watermark file or None if not found
            
        Assumptions:
            Searches for watermark files in predefined locations if custom path not set
            File system access is available for existence checks
        """
        
        if not self.enabled:
            return None
            
        path_to_check = self.watermark_path if self.watermark_path else self.default_watermark_path
        
        if os.path.exists(path_to_check):
            return path_to_check
            
        alternative_paths = [
            os.path.join(os.getcwd(), "brand", "logo.png"),
            os.path.join(os.getcwd(), "assets", "brand", "watermark.png"),
            os.path.join(os.getcwd(), "assets", "watermark.png"),
        ]
        
        for path in alternative_paths:
            if os.path.exists(path):
                return path
        
        return None



