"""HTML rendering module for ePy_docs.

Handles HTML-specific rendering logic using only JSON configuration.
"""
from typing import Optional, Dict, Any
import os
import subprocess

from ePy_docs.components.page import _ConfigManager


class HTMLRenderer:
    """Handles HTML rendering using Quarto with simple inline CSS from JSON config."""
    
    def __init__(self, styles_config: Optional[Dict[str, Any]] = None):
        """Initialize HTML renderer with styling configuration."""
        self.styles_config = styles_config or self._load_styles_config()
        self.pdf_settings = self.styles_config.get('pdf_settings', {})
    
    def _load_styles_config(self) -> Dict[str, Any]:
        """Load styles configuration from styles.json."""
        config_manager = _ConfigManager()
        config = config_manager.get_styles_config()
        if not config:
            return {
                'pdf_settings': {
                    'styles': {
                        'heading1': {'fontSize': 18, 'textColor': [198, 18, 60]},
                        'heading2': {'fontSize': 16, 'textColor': [0, 33, 126]},
                        'heading3': {'fontSize': 14, 'textColor': [99, 100, 102]},
                        'normal': {'fontSize': 12, 'textColor': [0, 0, 0]}
                    }
                }
            }
        return config
    
    def create_html_yaml_config(self, title: str, author: str) -> Dict[str, Any]:
        """Create HTML-specific YAML configuration."""
        return {
            'title': title,
            'author': author,
            'format': {
                'html': {
                    'toc': True,
                    'toc-depth': 3,
                    'number-sections': True,
                    'self-contained': True,
                    'embed-resources': True
                }
            }
        }
    
    def render_html(self, qmd_file: str, output_dir: Optional[str] = None) -> str:
        """Render QMD file to HTML."""
        qmd_path = os.path.abspath(qmd_file)
        if not os.path.exists(qmd_path):
            raise FileNotFoundError(f"QMD file not found: {qmd_path}")
        
        try:
            cmd = ['quarto', 'render', qmd_path, '--to', 'html']
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # Return expected HTML path
            qmd_basename = os.path.splitext(os.path.basename(qmd_path))[0]
            return os.path.join(os.path.dirname(qmd_path), f"{qmd_basename}.html")
            
        except subprocess.CalledProcessError as e:
            error_msg = f"Quarto HTML render failed: {e.stderr.strip() if e.stderr else 'Unknown error'}"
            raise RuntimeError(error_msg)
