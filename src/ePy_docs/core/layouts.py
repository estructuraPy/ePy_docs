"""Layout configurations for different types of reports.

Provides predefined layouts for academic, technical, and corporate reports
with appropriate formatting, margins, and styling options.
All configurations must be sourced from JSON files.
"""

import os
import json
from typing import Dict, Any, Optional
from enum import Enum

from ePy_docs.files.data import _load_cached_json


class ReportType(Enum):
    """Types of reports with different layout requirements."""
    ACADEMIC = "academic"
    TECHNICAL = "technical"
    CORPORATE = "corporate"
    MINIMAL = "minimal"


class ReportLayout:
    """Report layout manager for different report types."""
    
    def __init__(self, report_type: ReportType = ReportType.TECHNICAL):
        self.report_type = report_type
        self.layout_config = self._load_layout_config()
    
    def _load_layout_config(self) -> Dict[str, Any]:
        """Load layout configuration from JSON file - no fallbacks."""
        # Get the absolute path to layouts.json in the core directory
        import os
        current_dir = os.path.dirname(os.path.abspath(__file__))
        layouts_json_path = os.path.join(current_dir, "layouts.json")
        
        layouts_config = _load_cached_json(layouts_json_path)
        
        if not layouts_config:
            raise ValueError("layouts.json not found or empty")
        
        report_type_key = self.report_type.value
        if report_type_key not in layouts_config:
            raise ValueError(f"Layout configuration for '{report_type_key}' not found in layouts.json")
        
        config = layouts_config[report_type_key]
        
        # Validate required keys - fail if missing
        required_keys = ["margins", "font_size", "line_spacing", "header_style", "citation_style"]
        for key in required_keys:
            if key not in config:
                raise ValueError(f"Required key '{key}' missing in {report_type_key} layout configuration")
        
        # Validate margins structure
        margin_keys = ["top", "bottom", "left", "right"]
        for margin_key in margin_keys:
            if margin_key not in config["margins"]:
                raise ValueError(f"Required margin '{margin_key}' missing in {report_type_key} layout configuration")
        
        return config
    
    def get_quarto_yaml(self) -> Dict[str, Any]:
        """Generate Quarto YAML configuration from JSON data only."""
        config = {
            "format": {
                "pdf": {
                    "geometry": [
                        f"top={self.layout_config['margins']['top']}in",
                        f"bottom={self.layout_config['margins']['bottom']}in",
                        f"left={self.layout_config['margins']['left']}in",
                        f"right={self.layout_config['margins']['right']}in"
                    ],
                    "fontsize": f"{self.layout_config['font_size']}pt",
                    "linestretch": self.layout_config['line_spacing']
                }
            }
        }
        
        return config
    
    def apply_to_formatter(self, formatter) -> None:
        """Apply layout settings to a formatter instance."""
        # Apply header style
        if hasattr(formatter, 'header_style'):
            formatter.header_style = self.layout_config['header_style']
        
        # Apply citation style
        if hasattr(formatter, 'citation_style'):
            formatter.citation_style = self.layout_config['citation_style']
