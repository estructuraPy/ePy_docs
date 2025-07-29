"""Image processing and management for reports and presentations."""

import json
import os
import shutil
from pathlib import Path
from typing import Dict, Optional, Union

class ImageProcessor:
    """Processor for image handling across different output formats."""

    def __init__(self, config_path: Optional[str] = None):
        """Initialize ImageProcessor with configuration.
        
        Args:
            config_path: Path to the configuration file
        """
        self.config = self._load_config(config_path)
        self._counter = 1  # Initialize counter for auto-numbering

    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load configuration from JSON file.
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            Configuration dictionary
        """
        if not config_path:
            config_path = Path(__file__).parent / "images.json"
        
        try:
            with open(config_path) as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON in configuration file: {config_path}")

    def process_image(self, path: str, output_dir: str, title: Optional[str] = None, 
                     label: Optional[str] = None, counter: Optional[int] = None) -> str:
        """Process and organize an image with proper captioning.
        
        Args:
            path: Source image path
            output_dir: Base output directory
            title: Image title/caption
            label: Optional custom label for cross-referencing
            counter: Figure counter for numbering
            
        Returns:
            Processed image path with caption
        """
        if not os.path.exists(path):
            raise FileNotFoundError(f"Image file not found: {path}")

        if not self.validate_image_format(path):
            raise ValueError(f"Invalid image format: {path}")

        dest_path = self._organize_image(path, output_dir)
        caption = self._format_caption(title, counter)
        
        return self._create_image_reference(dest_path, caption, label)

    def _organize_image(self, path: str, output_dir: str) -> str:
        """Organize image into figures directory.
        
        Args:
            path: Source image path
            output_dir: Base output directory
            
        Returns:
            Organized image path
        """
        dest_dir = Path(output_dir) / "figures"
        dest_dir.mkdir(parents=True, exist_ok=True)
        
        dest_path = dest_dir / Path(path).name
        if path != str(dest_path):
            shutil.copy2(path, dest_path)
        
        return str(dest_path)

    def _format_caption(self, title: Optional[str], counter: Optional[int] = None) -> str:
        """Format image caption based on configuration.
        
        Args:
            title: Image title/caption
            counter: Figure counter for numbering
            
        Returns:
            Formatted caption
        """
        if not title:
            # Use figure_no_title_format for auto-generated figure labels
            if counter:
                return self.config["pagination"]["figure_no_title_format"].format(
                    counter=counter
                )
            return ""

        # Use figure_title_format when there's a title/caption
        return self.config["pagination"]["figure_title_format"].format(
            title=title
        )

    def _create_image_reference(self, path: str, caption: str, label: Optional[str] = None) -> str:
        """Create a cross-referenced image with caption.
        
        Args:
            path: Image path
            caption: Image caption
            label: Optional custom label for cross-referencing
            
        Returns:
            Image reference with caption
        """
        rel_path = self.get_relative_path(path, os.path.dirname(path))
        
        if self.config["cross_referencing"]["quarto_syntax"]:
            if label:
                fig_label = label
            else:
                # Generate automatic label if auto_numbering is enabled
                if self.config["cross_referencing"]["auto_numbering"]:
                    counter = getattr(self, '_counter', 1)
                    self._counter = counter + 1
                    prefix = self.config["cross_referencing"]["label_prefix"]
                    fig_label = f"#{prefix}{counter}"
                else:
                    fig_label = ""
            
            if caption and fig_label:
                return f"![{caption}]({rel_path}){{{fig_label}}}"
            elif caption:
                return f"![{caption}]({rel_path})"
            elif fig_label:
                return f"![]({rel_path}){{{fig_label}}}"
            else:
                return f"![]({rel_path})"
        
        # Non-Quarto syntax
        if caption:
            return f"![]({rel_path})\n*{caption}*"
        return f"![]({rel_path})"

    @staticmethod
    def get_relative_path(img_path: str, base_dir: str) -> str:
        """Get relative path for cross-platform compatibility.
        
        Args:
            img_path: Absolute image path
            base_dir: Base directory
            
        Returns:
            Relative path with forward slashes
        """
        return os.path.relpath(img_path, base_dir).replace('\\', '/')

    @staticmethod
    def organize_image(path: str, output_dir: str, subfolder: str = "figures") -> str:
        """Organize image into specified subdirectory (static method).
        
        Args:
            path: Source image path
            output_dir: Base output directory
            subfolder: Subdirectory name (default: "figures")
            
        Returns:
            Organized image path
        """
        import shutil
        dest_dir = Path(output_dir) / subfolder
        dest_dir.mkdir(parents=True, exist_ok=True)
        
        dest_path = dest_dir / Path(path).name
        if path != str(dest_path):
            shutil.copy2(path, dest_path)
        
        return str(dest_path)

    @staticmethod
    def validate_image_format(path: str, allowed_formats: Optional[list] = None) -> bool:
        """Validate image format.
        
        Args:
            path: Image file path
            allowed_formats: List of allowed extensions
            
        Returns:
            True if format is valid
        """
        if allowed_formats is None:
            allowed_formats = ['.png', '.jpg', '.jpeg', '.svg', '.pdf', '.webp']
        
        _, ext = os.path.splitext(path.lower())
        return ext in allowed_formats


def display_in_notebook(img_path: str, show_in_notebook: bool = True) -> None:
    """Display image in Jupyter notebook if available."""
    if not show_in_notebook:
        return
    try:
        from IPython.display import Image, display
        from IPython import get_ipython
        from ePy_docs.core.content import _load_cached_config
        if get_ipython() is not None:
            if os.path.exists(img_path):
                units_config = _load_cached_config('units')
                image_width = units_config['display']['formatting']['image_display_width']
                display(Image(img_path, width=image_width))
    except (ImportError, Exception):
        # Silently skip display if not in Jupyter or any other error
        pass
