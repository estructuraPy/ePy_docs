"""PDF rendering module for ePy_suite using Quarto.

Handles PDF-specific rendering logic and configuration.
All settings must come from JSON configuration files.
"""

import os
import subprocess
import shutil
from typing import Optional, Dict, Any

class PDFRenderer:
    """Handles PDF rendering using Quarto with configuration."""
    
    def __init__(self):
        """Initialize PDF renderer with styling configuration."""
        
        # Get project sync_files setting
        from ePy_docs.config.modular_loader import get_current_project_config
        current_config = get_current_project_config()
        
        # Load PDF settings using constitutional pattern
        from ePy_docs.internals.styling._pages import get_pages_config, _load_component_config
        
        page_config = get_pages_config()
        if not page_config:
            raise ValueError("Missing page configuration from components/pages.json")
        
        # Load report configuration for layout information  
        report_config = _load_component_config('report')
        if not report_config:
            # Provide default report configuration if not found
            report_config = {
                'layouts': {
                    'classic': {'margins': {'top': 1.0, 'bottom': 1.0, 'left': 1.0, 'right': 1.0}},
                    'academic': {'margins': {'top': 1.0, 'bottom': 1.0, 'left': 1.0, 'right': 1.0}},
                    'professional': {'margins': {'top': 1.0, 'bottom': 1.0, 'left': 1.0, 'right': 1.0}}
                }
            }
        
        try:
            # Get layout configuration for dynamic margins
            from ePy_docs.internals.styling._pages import get_current_layout
            layout_name = get_current_layout()
            
            # Ensure 'layouts' key exists in report_config
            if 'layouts' not in report_config:
                report_config['layouts'] = {
                    'classic': {'margins': {'top': 1.0, 'bottom': 1.0, 'left': 1.0, 'right': 1.0}}
                }
            
            # Use .get() with default margins if layout not found
            default_margins = {'top': 1.0, 'bottom': 1.0, 'left': 1.0, 'right': 1.0}
            current_layout = report_config['layouts'].get(layout_name, {'margins': default_margins})
            layout_margins = current_layout.get('margins', default_margins)
            
            # Convert inches to points for ReportLab (1 inch = 72 points)
            margin_top_pts = layout_margins['top'] * 72
            margin_bottom_pts = layout_margins['bottom'] * 72
            margin_left_pts = layout_margins['left'] * 72
            margin_right_pts = layout_margins['right'] * 72
            
            # Extract PDF-related settings from page config
            # Get settings from common format configuration with defaults
            default_format_config = {
                'common': {
                    'documentclass': 'article',
                    'papersize': 'letter',
                    'toc': True,
                    'toc-depth': 3,
                    'number-sections': True,
                    'colorlinks': True,
                    'fig-cap-location': 'bottom',
                    'tbl-cap-location': 'top'
                },
                'pdf': {
                    'fig-pos': 'H',
                    'tbl-pos': 'H'
                }
            }
            
            format_config = page_config.get('format', default_format_config)
            common_config = format_config.get('common', default_format_config['common'])
            pdf_config = format_config.get('pdf', default_format_config['pdf'])
            
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
    
    def _load_typography_config(self, header_style: str = "formal") -> Dict[str, Any]:
        """Load typography configuration from JSON files - NO FALLBACKS.
        
        Args:
            header_style: The header style to use ('formal', 'modern', 'branded', 'clean').
        """
        # Load configurations using constitutional pattern
        from ePy_docs.internals.styling._pages import _load_component_config
        from ePy_docs.internals.styling._colors import get_colors_config
        
        # Load text configuration - REQUIRED
        text_config = _load_component_config('text')
        if not text_config:
            raise ValueError("Missing text configuration from components/text.json")
        
        # Load colors configuration - REQUIRED  
        colors_config = get_colors_config()
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
        
        # NEW ARCHITECTURE: layout_config is directly in reports section
        reports_section = colors_config['reports']
        if 'layout_config' not in reports_section:
            raise ValueError("Missing 'layout_config' section in colors/reports configuration")
        
        text_colors = reports_section['layout_config']
        if not text_colors:
            raise ValueError("Empty 'layout_config' in colors/reports configuration")
        
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
    
    def create_pdf_yaml_config(self, title: str, author: str, header_style: str = "formal") -> Dict[str, Any]:
        """Create PDF-specific YAML configuration using styles.json.
        
        Args:
            title: Document title
            author: Document author
            header_style: The header style to use ('formal', 'modern', 'branded', 'clean').
            
        Returns:
            PDF configuration dictionary
        """
        margins = self.pdf_settings['margins']
        pagesize = self.pdf_settings['pagesize']
        
        # Load typography configuration
        styles = self._load_typography_config(header_style=header_style)
        
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
        
        # Get font configuration for LaTeX
        from ePy_docs.internals.styling._latex_builder import _get_font_latex_config
        from ePy_docs.internals.styling._pages import get_current_layout, _load_component_config
        
        # Get current layout to determine font family
        current_layout_name = get_current_layout()
        
        # Load layout configuration to get font family
        from ePy_docs.internals.styling._layout import LayoutCoordinator
        layout_config = LayoutCoordinator(current_layout_name)
        
        # Get font family from layout typography
        typography_data = layout_config.typography.get('typography', {})
        normal_font_config = typography_data.get('normal', {})
        h1_font_config = typography_data.get('h1', {})
        font_family = normal_font_config.get('family', h1_font_config.get('family', 'sans_modern'))
        
        # Generate LaTeX font configuration
        font_latex_config = _get_font_latex_config(font_family)
        
        # Split font config into lines for header-includes (remove empty lines)
        font_config_lines = [line for line in font_latex_config.strip().split('\n') if line.strip()]
        
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
        
        # Add font configuration to header (insert after package imports, before color definitions)
        if font_config_lines:
            # Insert font config after the package imports (after line 3)
            latex_header = latex_header[:3] + font_config_lines + latex_header[3:]
        
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
            check=False  # Don't raise immediately, let us handle the error
        )
        
        if result.returncode != 0:
            error_msg = f"Quarto PDF rendering failed (exit code {result.returncode}):\n"
            error_msg += f"STDOUT: {result.stdout}\n"
            error_msg += f"STDERR: {result.stderr}"
            raise RuntimeError(error_msg)
        
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
