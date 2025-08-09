"""PDF rendering module for ePy_suite using Quarto.

Handles PDF-specific rendering logic and configuration.
All settings must come from JSON configuration files.
"""

import os
import subprocess
import shutil
from typing import Optional, Dict, Any

from ePy_docs.styler.styler import _ConfigManager


class PDFRenderer:
    """Handles PDF rendering using Quarto with configuration from styles.json."""
    
    def __init__(self):
        """Initialize PDF renderer with styling configuration."""
        config_manager = _ConfigManager()
        self.styles_config = config_manager.get_styles_config()
        if not self.styles_config:
            raise ValueError("styles.json configuration not found")
        
        if 'pdf_settings' not in self.styles_config:
            raise ValueError("pdf_settings section missing in styles.json")
        
        self.pdf_settings = self.styles_config['pdf_settings']
    
    def _load_crossref_config(self) -> Dict[str, Any]:
        """Load crossref configuration from component JSON files."""
        config_manager = _ConfigManager()
        crossref_config = {}
        
        # Load images crossref
        images_config = config_manager.get_config_by_path('components/images.json')
        if images_config and 'crossref' in images_config:
            crossref_config.update(images_config['crossref'])
        
        # Load tables crossref
        tables_config = config_manager.get_config_by_path('components/tables.json')
        if tables_config and 'crossref' in tables_config:
            crossref_config.update(tables_config['crossref'])
        
        # Load equations crossref
        equations_config = config_manager.get_config_by_path('components/equations.json')
        if equations_config and 'crossref' in equations_config:
            crossref_config.update(equations_config['crossref'])
        
        return crossref_config
    
    def _load_typography_config(self) -> Dict[str, Any]:
        """Load typography configuration from text.json and colors.json."""
        config_manager = _ConfigManager()
        
        # Load text configuration from components/text.json
        text_config = config_manager.get_config_by_path('components/text.json')
        
        # Extract typography styles from headers and text sections
        headers_config = text_config['headers']
        text_section_config = text_config['text']
        
        # Load text colors from colors.json
        colors_config = config_manager.get_colors_config()
        text_colors = colors_config['reports']['text_colors']
        
        # Combine styles with colors - map h1->heading1, h2->heading2, h3->heading3 for LaTeX
        combined_styles = {}
        
        # Process headers (h1, h2, h3)
        header_mapping = {'h1': 'heading1', 'h2': 'heading2', 'h3': 'heading3'}
        for header_key, latex_key in header_mapping.items():
            if header_key in headers_config:
                combined_styles[latex_key] = headers_config[header_key].copy()
                if header_key in text_colors:
                    combined_styles[latex_key]['textColor'] = text_colors[header_key]
        
        # Process text styles (normal, caption)
        for style_name in ['normal', 'caption']:
            if style_name in text_section_config:
                combined_styles[style_name] = text_section_config[style_name].copy()
                if style_name in text_colors:
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
        
        # Create LaTeX header for custom styling and figure handling
        latex_header = f"""\\usepackage{{xcolor}}
\\usepackage{{float}}
\\usepackage{{caption}}
\\usepackage{{subcaption}}
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
  {{\\normalfont\\fontsize{{{heading3['fontSize']}}}{{{heading3['leading']}}}\\selectfont\\bfseries\\color{{heading3color}}}}}}
\\captionsetup[figure]{{position=bottom,labelfont=bf,textfont=normal}}
\\floatplacement{{figure}}{{H}}"""
        
        # Load crossref configuration from component files
        crossref_config = self._load_crossref_config()
        
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
                    'include-in-header': latex_header,
                    'fig-cap-location': self.pdf_settings['fig_cap_location'],
                    'fig-pos': self.pdf_settings['fig_pos'],
                    'crossref': crossref_config
                }
            },
            'crossref': crossref_config
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
