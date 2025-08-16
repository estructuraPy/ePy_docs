"""PDF rendering module for ePy_suite using Quarto.

Handles PDF-specific rendering logic and configuration.
All settings must come from JSON configuration files.
"""

import os
import subprocess
import shutil
from typing import Optional, Dict, Any

from ePy_docs.components.page import _ConfigManager


class PDFRenderer:
    """Handles PDF rendering using Quarto with configuration from styles.json."""
    
    def __init__(self):
        """Initialize PDF renderer with styling configuration."""
        config_manager = _ConfigManager()
        self.styles_config = config_manager.get_styles_config()
        
        # Require styles_config - NO fallbacks
        if not self.styles_config:
            raise ValueError("Missing styles configuration from components/page.json")
        
        # Load PDF settings from components/page.json using ConfigManager with sync_json
        page_config = config_manager.get_config_by_path('components/page.json', sync_json=True)
        if not page_config:
            raise ValueError("Missing page configuration from components/page.json")
        
        try:
            # Get layout configuration for dynamic margins
            if 'default_layout' not in page_config['format']:
                raise ValueError("Missing 'default_layout' in page.json format section")
            layout_name = page_config['format']['default_layout']
            if layout_name not in page_config['layouts']:
                raise ValueError(f"Layout '{layout_name}' not found in page.json")
            
            current_layout = page_config['layouts'][layout_name]
            layout_margins = current_layout['margins']
            
            # Convert inches to points for ReportLab (1 inch = 72 points)
            margin_top_pts = layout_margins['top'] * 72
            margin_bottom_pts = layout_margins['bottom'] * 72
            margin_left_pts = layout_margins['left'] * 72
            margin_right_pts = layout_margins['right'] * 72
            
            # Extract PDF-related settings from page config
            # Get settings from common format configuration
            if 'format' not in page_config:
                raise ValueError("Missing 'format' section in page.json")
            if 'common' not in page_config['format']:
                raise ValueError("Missing 'common' section in format configuration")
            if 'pdf' not in page_config['format']:
                raise ValueError("Missing 'pdf' section in format configuration")
                
            common_config = page_config['format']['common']
            pdf_config = page_config['format']['pdf']
            
            # Merge common and PDF-specific configurations
            merged_config = {**common_config, **pdf_config}
            
            self.pdf_settings = {
                "documentclass": merged_config['documentclass'],
                "pagesize": merged_config['papersize'],
                "toc": merged_config['toc'],
                "toc_depth": merged_config['toc-depth'],
                "number_sections": merged_config['number-sections'],
                "colorlinks": merged_config['colorlinks'],
                "fig_cap_location": merged_config['fig-cap-location'],
                "fig_pos": merged_config['fig-pos'],
                "margins": {
                    "top": margin_top_pts,
                    "bottom": margin_bottom_pts,
                    "left": margin_left_pts,
                    "right": margin_right_pts
                }
            }
        except Exception as e:
            raise ValueError(f"Error loading page configuration: {e}")
    
    def _load_typography_config(self) -> Dict[str, Any]:
        """Load typography configuration from JSON files - NO FALLBACKS."""
        config_manager = _ConfigManager()
        
        # Load text configuration - REQUIRED
        text_config = config_manager.get_config_by_path('components/text.json')
        if not text_config:
            raise ValueError("Missing text configuration from components/text.json")
        
        # Load colors configuration - REQUIRED  
        colors_config = config_manager.get_colors_config()
        if not colors_config:
            raise ValueError("Missing colors configuration from colors.json")
        
        # Extract required sections
        if 'headers' not in text_config:
            raise ValueError("Missing 'headers' section in components/text.json")
        headers_config = text_config['headers']
        if not headers_config:
            raise ValueError("Empty 'headers' section in components/text.json")
        
        if 'text' not in text_config:
            raise ValueError("Missing 'text' section in components/text.json")
        text_section_config = text_config['text']
        if not text_section_config:
            raise ValueError("Empty 'text' section in components/text.json")
        
        if 'reports' not in colors_config:
            raise ValueError("Missing 'reports' section in colors configuration")
        if 'text_colors' not in colors_config['reports']:
            raise ValueError("Missing 'text_colors' section in colors configuration")
        text_colors = colors_config['reports']['text_colors']
        if not text_colors:
            raise ValueError("Empty 'text_colors' section in colors configuration")
        
        # Process styles - NO DEFAULTS
        combined_styles = {}
        
        # Process headers (h1, h2, h3) - REQUIRED
        header_mapping = {'h1': 'heading1', 'h2': 'heading2', 'h3': 'heading3'}
        for header_key, latex_key in header_mapping.items():
            if header_key not in headers_config:
                raise ValueError(f"Missing '{header_key}' configuration in components/text.json headers")
            
            combined_styles[latex_key] = headers_config[header_key].copy()
            
            if header_key not in text_colors:
                raise ValueError(f"Missing '{header_key}' color configuration in colors.json")
            combined_styles[latex_key]['textColor'] = text_colors[header_key]
        
        # Process text styles (normal, caption) - REQUIRED
        for style_name in ['normal', 'caption']:
            if style_name not in text_section_config:
                raise ValueError(f"Missing '{style_name}' configuration in components/text.json text section")
                
            combined_styles[style_name] = text_section_config[style_name].copy()
            
            if style_name not in text_colors:
                raise ValueError(f"Missing '{style_name}' color configuration in colors.json")
            combined_styles[style_name]['textColor'] = text_colors[style_name]
        
        return combined_styles
    
    def create_pdf_yaml_config(self, title: str, author: str) -> Dict[str, Any]:
        """Create PDF-specific YAML configuration using styles.json.
        
        Args:
            title: Document title
            author: Document author
            
        Returns:
            PDF configuration dictionary
        """
        margins = self.pdf_settings['margins']
        pagesize = self.pdf_settings['pagesize']
        
        # Load typography configuration
        styles = self._load_typography_config()
        
        # Convert margins from points to inches
        margin_top = margins['top'] / 72
        margin_bottom = margins['bottom'] / 72
        margin_left = margins['left'] / 72
        margin_right = margins['right'] / 72
        
        heading1 = styles['heading1']
        heading2 = styles['heading2'] 
        heading3 = styles['heading3']
        normal = styles['normal']
        
        # Convert RGB colors to hex format
        def rgb_to_hex(rgb_list):
            return f"#{rgb_list[0]:02x}{rgb_list[1]:02x}{rgb_list[2]:02x}"
        
        h1_color = rgb_to_hex(heading1['textColor'])
        h2_color = rgb_to_hex(heading2['textColor'])
        h3_color = rgb_to_hex(heading3['textColor'])
        
        # Create LaTeX header for custom styling and figure handling as a list
        latex_header = [
            "\\usepackage{xcolor}",
            "\\usepackage{float}",
            "\\usepackage{caption}",
            "\\usepackage{subcaption}",
            f"\\definecolor{{heading1color}}{{HTML}}{{{h1_color[1:]}}}",
            f"\\definecolor{{heading2color}}{{HTML}}{{{h2_color[1:]}}}",
            f"\\definecolor{{heading3color}}{{HTML}}{{{h3_color[1:]}}}",
            "\\makeatletter",
            f"\\renewcommand{{\\section}}{{\\@startsection{{section}}{{1}}{{\\z@}}{{{heading1['spaceBefore']}pt}}{{{heading1['spaceAfter']}pt}}{{\\normalfont\\fontsize{{{heading1['fontSize']}}}{{{heading1['leading']}}}\\selectfont\\bfseries\\color{{heading1color}}}}}}",
            f"\\renewcommand{{\\subsection}}{{\\@startsection{{subsection}}{{2}}{{\\z@}}{{{heading2['spaceBefore']}pt}}{{{heading2['spaceAfter']}pt}}{{\\normalfont\\fontsize{{{heading2['fontSize']}}}{{{heading2['leading']}}}\\selectfont\\bfseries\\color{{heading2color}}}}}}",
            f"\\renewcommand{{\\subsubsection}}{{\\@startsection{{subsubsection}}{{3}}{{\\z@}}{{{heading3['spaceBefore']}pt}}{{{heading3['spaceAfter']}pt}}{{\\normalfont\\fontsize{{{heading3['fontSize']}}}{{{heading3['leading']}}}\\selectfont\\bfseries\\color{{heading3color}}}}}}",
            "\\makeatother",
            "\\captionsetup[figure]{position=bottom,labelfont=bf,textfont=normal}",
            "\\floatplacement{figure}{H}"
        ]
        
        return {
            'title': title,
            'author': author,
            'format': {
                'pdf': {
                    'documentclass': self.pdf_settings['documentclass'],
                    'geometry': [
                        f'top={margin_top}in',
                        f'bottom={margin_bottom}in',
                        f'left={margin_left}in',
                        f'right={margin_right}in'
                    ],
                    'papersize': pagesize,
                    'toc': self.pdf_settings['toc'],
                    'toc-depth': self.pdf_settings['toc_depth'],
                    'number-sections': self.pdf_settings['number_sections'],
                    'colorlinks': self.pdf_settings['colorlinks'],
                    'fontsize': f"{normal['fontSize']}pt",
                    'header-includes': latex_header,
                    'fig-cap-location': self.pdf_settings['fig_cap_location'],
                    'fig-pos': self.pdf_settings['fig_pos']
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
        
        if output_dir is None:
            output_dir = os.path.dirname(qmd_path)
        else:
            output_dir = os.path.abspath(output_dir)
            os.makedirs(output_dir, exist_ok=True)
        
        qmd_basename = os.path.splitext(os.path.basename(qmd_path))[0]
        expected_pdf = os.path.join(os.path.dirname(qmd_path), f"{qmd_basename}.pdf")
        final_pdf = os.path.join(output_dir, f"{qmd_basename}.pdf")
        
        result = subprocess.run(
            ['quarto', 'render', qmd_path, '--to', 'pdf'],
            cwd=os.path.dirname(qmd_path),
            capture_output=True,
            text=True,
            check=True
        )
        
        if output_dir != os.path.dirname(qmd_path) and os.path.exists(expected_pdf):
            shutil.move(expected_pdf, final_pdf)
        elif os.path.exists(expected_pdf):
            final_pdf = expected_pdf
        
        if not os.path.exists(final_pdf):
            raise RuntimeError("PDF was not generated")
        
        return final_pdf
    
    def get_pdf_settings(self) -> Dict[str, Any]:
        """Get PDF-specific settings from configuration.
        
        Returns:
            PDF settings dictionary
        """
        return self.pdf_settings.copy()
