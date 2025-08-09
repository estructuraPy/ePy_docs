"""HTML rendering module for ePy_docs - SIMPLIFIED VERSION.

Handles HTML-specific rendering logic using only JSON configuration.
No external CSS dependencies.
"""
from typing import Optional, Dict, Any
from pathlib import Path
import os
import subprocess

from ePy_docs.components.page import _ConfigManager


class HTMLRenderer:
    """Handles HTML rendering using Quarto with simple inline CSS from JSON config."""
    
    def __init__(self, styles_config: Optional[Dict[str, Any]] = None):
        """Initialize HTML renderer with styling configuration.
        
        Args:
            styles_config: Optional styles configuration override
        """
        self.styles_config = styles_config or self._load_styles_config()
        self.pdf_settings = self.styles_config.get('pdf_settings', {})
    
    def _load_styles_config(self) -> Dict[str, Any]:
        """Load styles configuration from styles.json."""
        config_manager = _ConfigManager()
        config = config_manager.get_styles_config()
        if not config:
            # Fallback default configuration
            return {
                'pdf_settings': {
                    'styles': {
                        'heading1': {'fontSize': 18, 'textColor': [198, 18, 60], 'spaceBefore': 12, 'spaceAfter': 6},
                        'heading2': {'fontSize': 16, 'textColor': [0, 33, 126], 'spaceBefore': 10, 'spaceAfter': 6},
                        'heading3': {'fontSize': 14, 'textColor': [99, 100, 102], 'spaceBefore': 8, 'spaceAfter': 4},
                        'normal': {'fontSize': 12, 'textColor': [0, 0, 0], 'leading': 14}
                    }
                }
            }
        return config
    
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
            if not rgb_list or len(rgb_list) != 3:
                return 'rgb(0, 0, 0)'
            return f"rgb({rgb_list[0]}, {rgb_list[1]}, {rgb_list[2]})"
        
        h1_color = rgb_to_css(heading1.get('textColor', [0, 0, 0]))
        h2_color = rgb_to_css(heading2.get('textColor', [0, 0, 0]))
        h3_color = rgb_to_css(heading3.get('textColor', [0, 0, 0]))
        
        # Create simple inline CSS - NO EXTERNAL FILES
        custom_css = f"""
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            font-size: {normal.get('fontSize', 12)}px;
            line-height: 1.6;
            color: {rgb_to_css(normal.get('textColor', [0, 0, 0]))};
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        h1 {{
            font-size: {heading1.get('fontSize', 18)}px;
            color: {h1_color};
            margin-top: {heading1.get('spaceBefore', 12)}px;
            margin-bottom: {heading1.get('spaceAfter', 6)}px;
            font-weight: bold;
        }}
        
        h2 {{
            font-size: {heading2.get('fontSize', 16)}px;
            color: {h2_color};
            margin-top: {heading2.get('spaceBefore', 10)}px;
            margin-bottom: {heading2.get('spaceAfter', 6)}px;
            font-weight: bold;
        }}
        
        h3 {{
            font-size: {heading3.get('fontSize', 14)}px;
            color: {h3_color};
            margin-top: {heading3.get('spaceBefore', 8)}px;
            margin-bottom: {heading3.get('spaceAfter', 4)}px;
            font-weight: bold;
        }}
        
        /* IMAGEN SIMPLE - SIN RECUADROS */
        .quarto-figure,
        .quarto-float,
        .figure {{
            margin: 15px 0 !important;
            padding: 0 !important;
            background: none !important;
            border: none !important;
            text-align: center !important;
        }}
        
        /* TAMAÑO FIJO SIMPLE */
        .quarto-figure img,
        .quarto-float img,
        .img-fluid,
        figure img {{
            max-width: 650px !important;
            width: auto !important;
            height: auto !important;
            margin: 10px auto !important;
            padding: 0 !important;
            border: 1px solid #ddd !important;
            border-radius: 3px !important;
            display: block !important;
        }}
        
        /* CAPTIONS SIMPLES */
        figcaption,
        .figure-caption {{
            font-size: 0.9em !important;
            color: #666 !important;
            text-align: center !important;
            margin: 8px 0 !important;
            font-style: italic !important;
        }}
        
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
            background-color: #f5f5f5;
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
                    'self-contained': True,
                    'embed-resources': True,
                    'fig-width': 5.0,
                    'fig-height': 3.8,
                    'fig-align': 'center',
                    'fig-responsive': True,
                    'fig-cap-location': 'bottom',
                    'tbl-cap-location': 'top',
                    'fig-dpi': 150,
                    'code-fold': False,
                    'code-tools': False
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
        
        # Create CSS in results directory if needed (not external dependency)
        if output_dir and 'results' in output_dir.lower():
            self._create_simple_css_in_results(output_dir)
        
        # Get expected HTML output path
        qmd_basename = os.path.splitext(os.path.basename(qmd_path))[0]
        expected_html = os.path.join(os.path.dirname(qmd_path), f"{qmd_basename}.html")
        final_html = os.path.join(output_dir, f"{qmd_basename}.html")
        
        try:
            # Run Quarto render
            cmd = ['quarto', 'render', qmd_path, '--to', 'html']
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # Move file if needed
            if expected_html != final_html and os.path.exists(expected_html):
                if os.path.exists(final_html):
                    os.remove(final_html)
                os.rename(expected_html, final_html)
            
            return final_html
            
        except subprocess.CalledProcessError as e:
            error_msg = f"Quarto HTML render failed: {e.stderr.strip() if e.stderr else 'Unknown error'}"
            raise RuntimeError(error_msg)
        except Exception as e:
            raise RuntimeError(f"Error during HTML rendering: {str(e)}")
    
    def _create_simple_css_in_results(self, output_dir: str) -> None:
        """Create simple CSS file in results directory using JSON configuration."""
        css_content = """/* CSS generado automáticamente desde configuración JSON */

/* Layout básico */
body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    line-height: 1.6;
    max-width: 900px;
    margin: 0 auto;
    padding: 20px;
}

/* CONTROL DE TAMAÑO DE IMÁGENES usando config JSON */
.quarto-figure,
.quarto-float,
.figure {
    margin: 15px 0 !important;
    padding: 0 !important;
    text-align: center !important;
    background: none !important;
    border: none !important;
}

/* Tamaño de imágenes optimizado */
.quarto-figure img,
.quarto-float img,
.img-fluid,
figure img {
    max-width: 100% !important;
    height: auto !important;
    margin: 10px auto !important;
    display: block !important;
    border: 1px solid #ddd !important;
    border-radius: 3px !important;
}

/* Captions */
figcaption,
.figure-caption {
    font-size: 0.9em !important;
    color: #666 !important;
    text-align: center !important;
    margin: 8px 0 !important;
    font-style: italic !important;
}

/* Tablas básicas */
table {
    border-collapse: collapse;
    width: 100%;
    margin: 15px 0;
}

th, td {
    border: 1px solid #ddd;
    padding: 8px;
    text-align: left;
}

th {
    background-color: #f5f5f5;
}
"""
        
        css_path = os.path.join(output_dir, 'auto_generated_styles.css')
        with open(css_path, 'w', encoding='utf-8') as f:
            f.write(css_content)
        
        print(f"CSS generado automáticamente en: {css_path}")
    
    def get_html_settings(self) -> Dict[str, Any]:
        """Get HTML-specific settings from configuration."""
        return {
            'fig_width': 6.5,
            'fig_height': 4.5,
            'fig_dpi': 200,
            'image_max_width': '650px',
            'use_external_css': False,
            'inline_css': True
        }
    
    def validate_html_config(self) -> bool:
        """Validate HTML configuration."""
        required_keys = ['pdf_settings']
        for key in required_keys:
            if key not in self.styles_config:
                return False
        return True
