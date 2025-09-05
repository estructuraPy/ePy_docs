"""PDF rendering module for ePy_suite using Quarto.

Handles PDF-specific rendering logic and configuration.
All settings must come from JSON configuration files.
"""

import os
import subprocess
import shutil
from typing import Optional, Dict, Any

from ePy_docs.components.pages import _ConfigManager
from ePy_docs.components.setup import _load_cached_files, _resolve_config_path

def get_pdf_config(sync_files: bool = False) -> Dict[str, Any]:
    """Load centralized PDF configuration.
    
    OFICINA COMERCIAL OFICIAL - Reino PDF
    
    Args:
        sync_files: Control cache synchronization behavior.
        
    Returns:
        Complete PDF configuration dictionary.
    """
    config_path = _resolve_config_path('components/pdf', sync_files)
    return _load_cached_files(config_path, sync_files)

class PDFRenderer:
    """Handles PDF rendering using Quarto with configuration from styles.json."""
    
    def __init__(self):
        """Initialize PDF renderer with styling configuration."""
        # Get current project config for sync_files setting
        from ePy_docs.components.setup import get_setup_config
        current_config = get_setup_config()
        self.sync_files = current_config.get('sync_files', False) if current_config else False
        
        # Load PDF Kingdom specific configuration
        self.pdf_config = get_pdf_config(sync_files=self.sync_files)
        
        # Load pages configuration - REQUIRED
        from ePy_docs.components.pages import get_pages_config
        self.pages_config = get_pages_config(self.sync_files)
        if not self.pages_config:
            raise ValueError("Missing pages configuration from components/pages.json")
        
        # Extract PDF settings
        if 'format' not in self.pages_config or 'pdf' not in self.pages_config['format']:
            raise ValueError("Missing 'format.pdf' section in pages configuration")
        self.pdf_settings = self.pages_config['format']['pdf']
        
        # Load additional configurations
        from ePy_docs.components.pages import get_pages_config
        page_config = get_pages_config(sync_files=self.sync_files)
        if not page_config:
            raise ValueError("Missing page configuration from components/pages.json")
        
        # Load report configuration for layout information
        report_config = get_pages_config(sync_files=self.sync_files)
        if not report_config:
            raise ValueError("Missing report configuration from components/report.json")
        
        try:
            # Get layout configuration for dynamic margins
            from ePy_docs.components.pages import get_layout_config
            current_layout = get_layout_config(sync_files=self.sync_files)
            layout_margins = current_layout['margins']
            
            # Convert inches to points for ReportLab (1 inch = 72 points)
            margin_top_pts = layout_margins['top'] * 72
            margin_bottom_pts = layout_margins['bottom'] * 72
            margin_left_pts = layout_margins['left'] * 72
            margin_right_pts = layout_margins['right'] * 72
            
            # Extract PDF-related settings from page config
            # Get settings from common format configuration
            if 'format' not in page_config:
                raise ValueError("Missing 'format' section in pages.json")
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
        
        # Load text configuration directly using get_text_config
        from ePy_docs.components.text import get_text_config
        text_config = get_text_config(sync_files=self.sync_files)
        if not text_config:
            raise ValueError("Missing text configuration from components/text.json")
        
        # Load colors configuration for text colors
        from ePy_docs.components.colors import get_colors_config
        colors_config = get_colors_config()
        if not colors_config:
            raise ValueError("Missing colors configuration from colors.json")
        
        # Get current layout for colors
        from ePy_docs.components.pages import get_layout_config
        current_layout = get_layout_config(sync_files=self.sync_files)
        current_layout_name = current_layout.get('name', 'minimal')  # Extract layout name
        
        # Extract text styles and colors
        layout_typography = text_config['layout_styles'][current_layout_name]['typography']
        text_section_config = layout_typography  # Use typography directly
        layout_styles = colors_config['reports']['layout_styles']
        text_colors = layout_styles[current_layout_name]
        
        # Check if this layout uses handwritten fonts for everything using Format Kingdom
        from ePy_docs.components.format import get_layout_font_requirements, generate_latex_font_commands
        font_requirements = get_layout_font_requirements(current_layout_name, sync_files=self.sync_files)
        uses_handwritten_everywhere = font_requirements['uses_handwritten_everywhere']
        
        # Convert margins from points to inches
        margin_top = margins['top'] / 72
        margin_bottom = margins['bottom'] / 72
        margin_left = margins['left'] / 72
        margin_right = margins['right'] / 72
        
        # Get text styles directly from layout typography configuration
        heading1 = layout_typography['h1'].copy()
        heading2 = layout_typography['h2'].copy()
        heading3 = layout_typography['h3'].copy()
        normal = layout_typography['normal'].copy()
        
        # Add default values for PDF rendering if missing
        def add_pdf_defaults(style_config, default_font_size):
            if 'fontSize' not in style_config:
                size_str = style_config.get('size', f'{default_font_size}pt')
                style_config['fontSize'] = int(size_str.replace('pt', ''))
            if 'spaceBefore' not in style_config:
                style_config['spaceBefore'] = style_config['fontSize'] * 0.5
            if 'spaceAfter' not in style_config:
                style_config['spaceAfter'] = style_config['fontSize'] * 0.3
            if 'leading' not in style_config:
                style_config['leading'] = style_config['fontSize'] * 1.2
            return style_config
        
        heading1 = add_pdf_defaults(heading1, 18)
        heading2 = add_pdf_defaults(heading2, 16)
        heading3 = add_pdf_defaults(heading3, 14)
        normal = add_pdf_defaults(normal, 12)
        
        # Combine text styles with colors
        heading1['textColor'] = text_colors['h1']
        heading2['textColor'] = text_colors['h2']
        heading3['textColor'] = text_colors['h3']
        
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
        ]
        
        # Add universal font configuration from Format Kingdom
        font_commands = generate_latex_font_commands(current_layout_name, sync_files=self.sync_files)
        latex_header.extend(font_commands)
        
        # Add PDF Kingdom specific configurations
        pdf_engine_config = self.pdf_config['pdf_engine']
        if pdf_engine_config['fontspec_enabled']:
            # fontspec already included in font_commands, add any additional configuration
            pass
        
        # Add PDF-specific packages based on configuration
        if self.pdf_config['pdf_specific']['hyperref']:
            latex_header.append("\\usepackage{hyperref}")
        
        if self.pdf_config['pdf_specific']['bookmarks']:
            latex_header.append("\\usepackage{bookmark}")
        
        # Add debugging options if enabled
        if self.pdf_config['debugging']['verbose_logging']:
            latex_header.append("\\errorstopmode")  # Stop on errors for debugging
        
        # Add color definitions and styling
        latex_header.extend([
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
        ])
        
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
