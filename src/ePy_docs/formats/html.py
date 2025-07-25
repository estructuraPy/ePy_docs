"""HTML rendering module for ePy_docs using Quarto.

Handles HTML-specific rendering logic and configuration.
"""

import os
import subprocess
import shutil
from typing import Optional, Dict, Any
from pathlib import Path

from ePy_docs.styler.setup import _ConfigManager


class HTMLRenderer:
    """Handles HTML rendering using Quarto with configuration from styles.json."""
    
    def __init__(self, styles_config: Optional[Dict[str, Any]] = None):
        """Initialize HTML renderer with styling configuration.
        
        Args:
            styles_config: Optional styles configuration override
        """
        self.styles_config = styles_config or self._load_styles_config()
        self.pdf_settings = self.styles_config.get('pdf_settings', {})
    
    def _load_styles_config(self) -> Dict[str, Any]:
        """Load styles configuration from styles.json."""
        try:
            config_manager = _ConfigManager()
            return config_manager.get_styles_config()
        except Exception as e:
            raise ValueError(f"Failed to load styles configuration: {e}")
    
    def create_html_yaml_config(self, title: str, author: str) -> Dict[str, Any]:
        """Create HTML-specific YAML configuration using styles.json.
        
        Args:
            title: Document title
            author: Document author
            
        Returns:
            HTML configuration dictionary
        """
        # Get heading styles for custom formatting
        styles = self.pdf_settings.get('styles', {})
        heading1 = styles.get('heading1', {})
        heading2 = styles.get('heading2', {})
        heading3 = styles.get('heading3', {})
        normal = styles.get('normal', {})
        
        # Convert RGB colors to CSS format
        def rgb_to_css(rgb_list):
            if isinstance(rgb_list, list) and len(rgb_list) == 3:
                return f"rgb({rgb_list[0]}, {rgb_list[1]}, {rgb_list[2]})"
            return "rgb(0, 0, 0)"
        
        h1_color = rgb_to_css(heading1.get('textColor', [0, 0, 0]))
        h2_color = rgb_to_css(heading2.get('textColor', [0, 0, 0]))
        h3_color = rgb_to_css(heading3.get('textColor', [0, 0, 0]))
        
        # Create CSS for custom styling
        custom_css = f"""
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif;
            font-size: {normal.get('fontSize', 12)}px;
            line-height: {normal.get('leading', 14) / normal.get('fontSize', 12)};
            color: {rgb_to_css(normal.get('textColor', [0, 0, 0]))};
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        h1 {{
            font-size: {heading1.get('fontSize', 18)}px;
            line-height: {heading1.get('leading', 22) / heading1.get('fontSize', 18)};
            color: {h1_color};
            margin-top: {heading1.get('spaceBefore', 12)}px;
            margin-bottom: {heading1.get('spaceAfter', 6)}px;
            font-weight: bold;
        }}
        
        h2 {{
            font-size: {heading2.get('fontSize', 16)}px;
            line-height: {heading2.get('leading', 20) / heading2.get('fontSize', 16)};
            color: {h2_color};
            margin-top: {heading2.get('spaceBefore', 10)}px;
            margin-bottom: {heading2.get('spaceAfter', 6)}px;
            font-weight: bold;
        }}
        
        h3 {{
            font-size: {heading3.get('fontSize', 14)}px;
            line-height: {heading3.get('leading', 17) / heading3.get('fontSize', 14)};
            color: {h3_color};
            margin-top: {heading3.get('spaceBefore', 8)}px;
            margin-bottom: {heading3.get('spaceAfter', 4)}px;
            font-weight: bold;
        }}
        
        .table-of-contents {{
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }}
        
        .table-of-contents ul {{
            list-style-type: none;
            padding-left: 0;
        }}
        
        .table-of-contents li {{
            margin: 5px 0;
        }}
        
        .table-of-contents a {{
            text-decoration: none;
            color: #007bff;
        }}
        
        .table-of-contents a:hover {{
            text-decoration: underline;
        }}
        
        /* General image styling - SUBTLE SIZING */
        img {{
            max-width: 100%;
            height: auto;
            display: block;
            margin: 15px auto;
        }}
        
        /* SUBTLE TABLE FIGURE STYLING */
        .quarto-figure {{
            text-align: center;
            margin: 20px 0;
            padding: 10px;
            background-color: #fbfbfb;
            border-radius: 4px;
            border: 1px solid #e9ecef;
        }}
        
        .quarto-figure img,
        .table-figure img,
        .plot-figure img {{
            max-width: 65% !important;
            width: auto !important;
            height: auto !important;
            border: 1px solid #dee2e6 !important;
            border-radius: 4px !important;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
            margin: 10px auto !important;
            background-color: white !important;
            padding: 5px !important;
        }}
        
        .quarto-figure-center {{
            display: flex !important;
            flex-direction: column !important;
            align-items: center !important;
            margin: 20px 0 !important;
            padding: 15px !important;
            background: white !important;
            border-radius: 4px !important;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1) !important;
        }}
        
        /* SUBTLE TABLE STYLING */
        .table-figure img {{
            border: 1px solid #28a745 !important;
            box-shadow: 0 2px 4px rgba(40,167,69,0.15) !important;
            background-color: #f8fff9 !important;
        }}
        
        /* SUBTLE PLOT STYLING */
        .plot-figure img {{
            border: 1px solid #007bff !important;
            box-shadow: 0 2px 4px rgba(0,123,255,0.15) !important;
            background-color: #f8f9fa !important;
        }}
        
        /* SUBTLE CAPTION STYLING */
        .quarto-figure figcaption,
        .figure-caption {{
            font-size: 0.9em !important;
            color: #6c757d !important;
            text-align: center !important;
            margin-top: 8px !important;
            margin-bottom: 10px !important;
            font-weight: normal !important;
            font-style: italic !important;
            background-color: transparent !important;
            padding: 5px 10px !important;
            border-radius: 0 !important;
            max-width: 85% !important;
            margin-left: auto !important;
            margin-right: auto !important;
        }}
        
        /* RESPONSIVE - SUBTLE */
        @media screen and (max-width: 768px) {{
            .quarto-figure img,
            .table-figure img,
            .plot-figure img {{
                max-width: 80% !important;
                border-width: 1px !important;
            }}
            
            .quarto-figure-center {{
                padding: 10px !important;
                margin: 15px 0 !important;
            }}
            
            .quarto-figure figcaption,
            .figure-caption {{
                font-size: 0.85em !important;
                max-width: 90% !important;
                padding: 4px 8px !important;
            }}
        }}
        
        @media screen and (max-width: 480px) {{
            .quarto-figure img,
            .table-figure img,
            .plot-figure img {{
                max-width: 90% !important;
                margin: 8px auto !important;
            }}
            
            .quarto-figure figcaption,
            .figure-caption {{
                font-size: 0.8em !important;
                padding: 3px 6px !important;
            }}
        }}
        
        /* LARGE SCREEN - PROPORTIONAL TABLES */
        @media screen and (min-width: 1200px) {{
            .quarto-figure img,
            .table-figure img,
            .plot-figure img {{
                max-width: 60% !important;
            }}
            
            .quarto-figure-center {{
                padding: 20px !important;
                margin: 50px 0 !important;
            }}
        }}
        
        /* Traditional HTML table styling (for actual tables, not images) */
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 15px 0;
        }}
        
        th, td {{
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }}
        
        th {{
            background-color: #f2f2f2;
            font-weight: bold;
        }}
        
        code {{
            background-color: #f4f4f4;
            padding: 2px 4px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }}
        
        pre {{
            background-color: #f4f4f4;
            padding: 10px;
            border-radius: 5px;
            overflow-x: auto;
        }}
        
        blockquote {{
            border-left: 4px solid #ddd;
            padding-left: 15px;
            margin: 15px 0;
            font-style: italic;
        }}
        """
        
        return {
            'title': title,
            'author': author,
            'format': {
                'html': {
                    'toc': True,
                    'toc-depth': 3,
                    'number-sections': True,
                    'theme': 'default',
                    'css': custom_css,
                    'self-contained': True,
                    'embed-resources': True,
                    'fig-width': 10.0,
                    'fig-height': 'auto',
                    'fig-align': 'center',
                    'fig-responsive': True,
                    'fig-cap-location': 'bottom',
                    'tbl-cap-location': 'bottom'
                }
            },
            'execute': {
                'echo': False,
                'warning': False,
                'error': False
            },
            'crossref': {
                'fig-title': 'Figura',
                'tbl-title': 'Tabla',
                'fig-prefix': 'Figura',
                'tbl-prefix': 'Tabla'
            }
        }
    
    def render_html(self, qmd_file: str, output_dir: Optional[str] = None) -> str:
        """Render QMD file to HTML.
        
        Args:
            qmd_file: Path to the .qmd file
            output_dir: Optional output directory
            
        Returns:
            Path to the generated HTML file
        """
        qmd_path = os.path.abspath(qmd_file)
        if not os.path.exists(qmd_path):
            raise FileNotFoundError(f"QMD file not found: {qmd_path}")
        
        # Determine output directory
        if output_dir is None:
            output_dir = os.path.dirname(qmd_path)
        else:
            output_dir = os.path.abspath(output_dir)
            os.makedirs(output_dir, exist_ok=True)
        
        # Get expected HTML output path
        qmd_basename = os.path.splitext(os.path.basename(qmd_path))[0]
        expected_html = os.path.join(os.path.dirname(qmd_path), f"{qmd_basename}.html")
        final_html = os.path.join(output_dir, f"{qmd_basename}.html")
        
        try:
            # Run quarto render command for HTML
            result = subprocess.run(
                ['quarto', 'render', qmd_path, '--to', 'html'],
                cwd=os.path.dirname(qmd_path),
                capture_output=True,
                text=True,
                check=True
            )
            
            # Move HTML to desired output directory if different
            if output_dir != os.path.dirname(qmd_path) and os.path.exists(expected_html):
                shutil.move(expected_html, final_html)
            elif os.path.exists(expected_html):
                final_html = expected_html
            
            if not os.path.exists(final_html):
                raise RuntimeError("HTML was not generated successfully")
            
            return final_html
            
        except subprocess.CalledProcessError as e:
            error_msg = f"Quarto HTML render failed: {e.stderr.strip() if e.stderr else 'Unknown error'}"
            raise RuntimeError(error_msg)
        except Exception as e:
            raise RuntimeError(f"Error during HTML rendering: {str(e)}")
    
    def get_html_settings(self) -> Dict[str, Any]:
        """Get HTML-specific settings from configuration.
        
        Returns:
            HTML settings dictionary based on PDF settings
        """
        return {
            'styles': self.pdf_settings.get('styles', {}),
            'theme': 'default',
            'self_contained': True,
            'embed_resources': True
        }
    
    def validate_html_config(self) -> bool:
        """Validate HTML configuration.
        
        Returns:
            True if configuration is valid
        """
        # HTML uses same styles as PDF, so validate those
        styles = self.pdf_settings.get('styles', {})
        required_styles = ['heading1', 'heading2', 'heading3', 'normal']
        for style in required_styles:
            if style not in styles:
                return False
        
        return True
