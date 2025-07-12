"""PDF rendering module for ePy_suite using Quarto.

Handles PDF-specific rendering logic and configuration.
All settings must come from JSON configuration files.
"""

import os
import subprocess
import shutil
from typing import Optional, Dict, Any
from pathlib import Path

from ePy_suite.files.styler.setup import _ConfigManager


class PDFRenderer:
    """Handles PDF rendering using Quarto with configuration from styles.json."""
    
    def __init__(self, styles_config: Optional[Dict[str, Any]] = None):
        """Initialize PDF renderer with styling configuration.
        
        Args:
            styles_config: Optional styles configuration override
        """
        self.styles_config = styles_config or self._load_styles_config()
        self.pdf_settings = self._get_pdf_settings()
    
    def _load_styles_config(self) -> Dict[str, Any]:
        """Load styles configuration from styles.json."""
        config_manager = _ConfigManager()
        config = config_manager.get_styles_config()
        if not config:
            raise ValueError("Failed to load styles configuration from styles.json")
        return config
    
    def _get_pdf_settings(self) -> Dict[str, Any]:
        """Get PDF settings from configuration."""
        if 'pdf_settings' not in self.styles_config:
            raise ValueError("pdf_settings section missing in styles.json")
        return self.styles_config['pdf_settings']
    
    def create_pdf_yaml_config(self, title: str, author: str) -> Dict[str, Any]:
        """Create PDF-specific YAML configuration using styles.json.
        
        Args:
            title: Document title
            author: Document author
            
        Returns:
            PDF configuration dictionary
        """
        if not title:
            raise ValueError("Title is required")
        if not author:
            raise ValueError("Author is required")
        
        if 'margins' not in self.pdf_settings:
            raise ValueError("margins section missing in pdf_settings")
        if 'pagesize' not in self.pdf_settings:
            raise ValueError("pagesize missing in pdf_settings")
        
        margins = self.pdf_settings['margins']
        pagesize = self.pdf_settings['pagesize']
        
        # Validate margin keys
        required_margins = ['top', 'bottom', 'left', 'right']
        for margin_key in required_margins:
            if margin_key not in margins:
                raise ValueError(f"Margin '{margin_key}' missing in pdf_settings.margins")
        
        # Convert margins from points to inches (72 points = 1 inch)
        margin_top = margins['top'] / 72
        margin_bottom = margins['bottom'] / 72
        margin_left = margins['left'] / 72
        margin_right = margins['right'] / 72
        
        # Validate styles section
        if 'styles' not in self.pdf_settings:
            raise ValueError("styles section missing in pdf_settings")
        
        styles = self.pdf_settings['styles']
        required_styles = ['heading1', 'heading2', 'heading3', 'normal']
        for style_name in required_styles:
            if style_name not in styles:
                raise ValueError(f"Style '{style_name}' missing in pdf_settings.styles")
        
        heading1 = styles['heading1']
        heading2 = styles['heading2'] 
        heading3 = styles['heading3']
        normal = styles['normal']
        
        # Validate required style properties
        style_properties = ['textColor', 'fontSize', 'leading', 'spaceBefore', 'spaceAfter']
        for style_name, style_config in [('heading1', heading1), ('heading2', heading2), ('heading3', heading3), ('normal', normal)]:
            for prop in style_properties:
                if prop not in style_config:
                    raise ValueError(f"Property '{prop}' missing in {style_name} style configuration")
        
        # Convert RGB colors to hex format
        def rgb_to_hex(rgb_list):
            if not isinstance(rgb_list, list) or len(rgb_list) != 3:
                raise ValueError("textColor must be a list of 3 RGB values")
            return f"#{rgb_list[0]:02x}{rgb_list[1]:02x}{rgb_list[2]:02x}"
        
        h1_color = rgb_to_hex(heading1['textColor'])
        h2_color = rgb_to_hex(heading2['textColor'])
        h3_color = rgb_to_hex(heading3['textColor'])
        
        # Create LaTeX header for custom styling
        latex_header = f"""\\usepackage{{xcolor}}
\\definecolor{{heading1color}}{{HTML}}{{{h1_color[1:]}}}
\\definecolor{{heading2color}}{{HTML}}{{{h2_color[1:]}}}
\\definecolor{{heading3color}}{{HTML}}{{{h3_color[1:]}}}
\\renewcommand{{\\section}}{{\\@startsection{{section}}{{1}}{{\\z@}}%
  {{{heading1['spaceBefore']}pt}}%
  {{{heading1['spaceAfter']}pt}}%
  {{\\normalfont\\fontsize{{{heading1['fontSize']}}}{{{heading1['leading']}}}\\selectfont\\bfseries\\color{{heading1color}}}}}}
\\renewcommand{{\\subsection}}{{\\@startsection{{subsection}}{{2}}{{\\z@}}%
  {{{heading2['spaceBefore']}pt}}%
  {{{heading2['spaceAfter']}pt}}%
  {{\\normalfont\\fontsize{{{heading2['fontSize']}}}{{{heading2['leading']}}}\\selectfont\\bfseries\\color{{heading2color}}}}}}
\\renewcommand{{\\subsubsection}}{{\\@startsection{{subsubsection}}{{3}}{{\\z@}}%
  {{{heading3['spaceBefore']}pt}}%
  {{{heading3['spaceAfter']}pt}}%
  {{\\normalfont\\fontsize{{{heading3['fontSize']}}}{{{heading3['leading']}}}\\selectfont\\bfseries\\color{{heading3color}}}}}}"""
        
        return {
            'title': title,
            'author': author,
            'format': {
                'pdf': {
                    'documentclass': 'article',
                    'geometry': [
                        f'top={margin_top}in',
                        f'bottom={margin_bottom}in',
                        f'left={margin_left}in',
                        f'right={margin_right}in'
                    ],
                    'papersize': pagesize,
                    'toc': True,
                    'toc-depth': 3,
                    'number-sections': True,
                    'colorlinks': True,
                    'fontsize': f"{normal['fontSize']}pt",
                    'include-in-header': latex_header
                }
            }
        }
    
    def render_pdf(self, qmd_file: str, output_dir: Optional[str] = None) -> str:
        """Render QMD file to PDF.
        
        Args:
            qmd_file: Path to the .qmd file
            output_dir: Optional output directory
            
        Returns:
            Path to the generated PDF file
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
        
        # Get expected PDF output path
        qmd_basename = os.path.splitext(os.path.basename(qmd_path))[0]
        expected_pdf = os.path.join(os.path.dirname(qmd_path), f"{qmd_basename}.pdf")
        final_pdf = os.path.join(output_dir, f"{qmd_basename}.pdf")
        
        try:
            # Run quarto render command for PDF
            result = subprocess.run(
                ['quarto', 'render', qmd_path, '--to', 'pdf'],
                cwd=os.path.dirname(qmd_path),
                capture_output=True,
                text=True,
                check=True
            )
            
            # Move PDF to desired output directory if different
            if output_dir != os.path.dirname(qmd_path) and os.path.exists(expected_pdf):
                shutil.move(expected_pdf, final_pdf)
            elif os.path.exists(expected_pdf):
                final_pdf = expected_pdf
            
            if not os.path.exists(final_pdf):
                raise RuntimeError("PDF was not generated successfully")
            
            return final_pdf
            
        except subprocess.CalledProcessError as e:
            error_msg = f"Quarto PDF render failed: {e.stderr.strip() if e.stderr else 'Unknown error'}"
            raise RuntimeError(error_msg)
        except Exception as e:
            raise RuntimeError(f"Error during PDF rendering: {str(e)}")
    
    def get_pdf_settings(self) -> Dict[str, Any]:
        """Get PDF-specific settings from configuration.
        
        Returns:
            PDF settings dictionary
        """
        return self.pdf_settings.copy()
    
    def validate_pdf_config(self) -> bool:
        """Validate PDF configuration.
        
        Returns:
            True if configuration is valid
        """
        required_keys = ['margins', 'pagesize', 'styles']
        for key in required_keys:
            if key not in self.pdf_settings:
                return False
        
        # Check margin values
        margins = self.pdf_settings.get('margins', {})
        margin_keys = ['top', 'bottom', 'left', 'right']
        for margin_key in margin_keys:
            if margin_key not in margins:
                return False
            if not isinstance(margins[margin_key], (int, float)):
                return False
        
        # Check styles
        styles = self.pdf_settings.get('styles', {})
        required_styles = ['heading1', 'heading2', 'heading3', 'normal']
        for style in required_styles:
            if style not in styles:
                return False
        
        return True
