"""LaTeX Configuration and Rendering Auxiliary Module for ePy_docs.

This auxiliary module contains LaTeX generation functions and the PDFRenderer class
for document styling and PDF generation. Used by styler.py (public API).
"""
from typing import Dict, Any, List, Optional
from pathlib import Path
import os
import shutil
import subprocess

from ePy_docs.internals.data_processing._data import _safe_get_nested


def _get_classoptions_for_layout(layout_name: str, page_config: Dict[str, Any], document_type: str = 'report') -> Optional[List[str]]:
    """Get LaTeX class options based on layout configuration.
    
    Args:
        layout_name: Name of the layout to use
        page_config: Configuration from pages.json
        document_type: Type of document ('report' or 'paper')
        
    Returns:
        List of class options or None if single column
        
    Note:
        Two-column layout is only applied to papers (articles), not reports (books).
        Reports always use single column layout regardless of layout configuration.
    """
    if not page_config or 'layouts' not in page_config:
        return None
    
    # IMPORTANT: Reports (books) should always use single column
    # Two-column layout is only for papers (articles)
    if document_type == 'report':
        return None
        
    layout_config = page_config['layouts'].get(layout_name, {})
    column_count = layout_config.get('column_count', 1)
    
    if column_count == 2:
        return ["twocolumn"]
    elif column_count > 2:
        # For more than 2 columns, we'll use multicol package in the LaTeX header
        # but not set classoption to avoid conflicts
        return None
    else:
        # Single column (default)
        return None


def _get_figure_width_for_layout(layout_name: str, page_config: Dict[str, Any], images_config: Dict[str, Any]) -> float:
    """Get figure width based on layout configuration.
    
    Args:
        layout_name: Name of the layout to use
        page_config: Configuration from pages.json
        images_config: Configuration from images.json
        
    Returns:
        Figure width in inches
    """
    if not page_config or 'layouts' not in page_config:
        return _safe_get_nested(images_config, 'display.max_width_inches', 6.5)
        
    layout_config = page_config['layouts'].get(layout_name, {})
    column_count = layout_config.get('column_count', 1)
    
    if column_count >= 2:
        # Multi-column layout: use narrower figures
        return _safe_get_nested(images_config, 'display.two_column_layout.pdf.max_width_inches', 3.5)
    else:
        # Single column layout: use full width figures
        return _safe_get_nested(images_config, 'display.max_width_inches', 6.5)


def _get_figure_height_for_layout(layout_name: str, page_config: Dict[str, Any], images_config: Dict[str, Any]) -> float:
    """Get figure height based on layout configuration.
    
    Args:
        layout_name: Name of the layout to use
        page_config: Configuration from pages.json
        images_config: Configuration from images.json
        
    Returns:
        Figure height in inches
    """
    if not page_config or 'layouts' not in page_config:
        return _safe_get_nested(images_config, 'display.max_width_inches', 6.5) * 0.65
        
    layout_config = page_config['layouts'].get(layout_name, {})
    column_count = layout_config.get('column_count', 1)
    
    if column_count >= 2:
        # Multi-column layout: use narrower figures
        return _safe_get_nested(images_config, 'display.two_column_layout.pdf.max_height_inches', 2.3)
    else:
        # Single column layout: use full width figures
        return _safe_get_nested(images_config, 'display.max_width_inches', 6.5) * 0.65


def _generate_multicol_config(layout_name: str, page_config: Dict[str, Any], images_config: dict = None) -> str:
    """Generate LaTeX configuration for multi-column layout."""
    if not page_config or 'layouts' not in page_config:
        return ""
        
    layout_config = page_config['layouts'].get(layout_name, {})
    column_count = layout_config.get('column_count', 1)
    
    if column_count >= 2:
        # Get column spacing from images configuration
        if images_config:
            column_sep = _safe_get_nested(images_config, 'display.two_column_layout.pdf.inter_column_space', '1.5em')
        else:
            column_sep = '1.5em'
            
        return f'''
% Multi-column layout configuration
\\usepackage{{multicol}}
\\usepackage{{balance}}
\\setlength{{\\columnsep}}{{{column_sep}}}
\\setlength{{\\columnseprule}}{{0pt}}
'''
    return ""


def _generate_header_footer_latex(page_layout_config: Dict[str, Any], 
                                 project_config: Dict[str, Any], 
                                 copyright_info: Dict[str, Any], 
                                 layout_name: str) -> str:
    """Generate LaTeX header/footer configuration based on page layout.
    
    Args:
        page_layout_config: Page layout configuration from pages.json
        project_config: Project configuration
        copyright_info: Copyright information
        layout_name: Current layout name
        
    Returns:
        str: LaTeX header/footer configuration string
    """
    if not page_layout_config:
        # Fallback to basic header/footer if no page layout config
        return rf'''
\lhead{{\textcolor{{headercolor}}{{{project_config['client']['name']}}}}}
\chead{{}}        
\rhead{{\textcolor{{headercolor}}{{{copyright_info['name']}}}}}
\lfoot{{}}
\cfoot{{\textcolor{{pagenumbercolor}}{{\thepage}}}}
\rfoot{{}}
'''
    
    # Get header and footer content specifications
    header_content = page_layout_config.get('header_content', 'project_client')
    footer_content = page_layout_config.get('footer_content', 'page_number')
    
    # Generate header content based on specification
    left_header = ""
    center_header = ""
    right_header = ""
    
    if header_content == 'project_client':
        left_header = rf'\textcolor{{headercolor}}{{{project_config["client"]["name"]}}}'
        right_header = rf'\textcolor{{headercolor}}{{{copyright_info["name"]}}}'
    elif header_content == 'project_name':
        left_header = rf'\textcolor{{headercolor}}{{{project_config["project"]["name"]}}}'
    elif header_content == 'company_name':
        center_header = rf'\textcolor{{headercolor}}{{{copyright_info["name"]}}}'
    elif header_content == 'minimal':
        # Minimal header - keep empty
        pass
    elif header_content == 'document_title':
        center_header = rf'\textcolor{{headercolor}}{{\leftmark}}'
    elif header_content == 'institution_name':
        left_header = rf'\textcolor{{headercolor}}{{{copyright_info["name"]}}}'
    
    # Generate footer content based on specification
    left_footer = ""
    center_footer = ""
    right_footer = ""
    
    if footer_content == 'page_number':
        center_footer = rf'\textcolor{{pagenumbercolor}}{{\thepage}}'
    elif footer_content == 'page_number_title':
        left_footer = rf'\textcolor{{pagenumbercolor}}{{\leftmark}}'
        center_footer = rf'\textcolor{{pagenumbercolor}}{{\thepage}}'
    elif footer_content == 'page_number_confidential':
        left_footer = rf'\textcolor{{pagenumbercolor}}{{Confidential}}'
        center_footer = rf'\textcolor{{pagenumbercolor}}{{\thepage}}'
    elif footer_content == 'page_number_only':
        center_footer = rf'\textcolor{{pagenumbercolor}}{{\thepage}}'
    elif footer_content == 'page_number_date':
        left_footer = rf'\textcolor{{pagenumbercolor}}{{\today}}'
        center_footer = rf'\textcolor{{pagenumbercolor}}{{\thepage}}'
    elif footer_content == 'page_number_author':
        left_footer = rf'\textcolor{{pagenumbercolor}}{{{project_config["project"]["created_date"]}}}'
        center_footer = rf'\textcolor{{pagenumbercolor}}{{\thepage}}'
    
    return rf'''
\lhead{{{left_header}}}
\chead{{{center_header}}}        
\rhead{{{right_header}}}
\lfoot{{{left_footer}}}
\cfoot{{{center_footer}}}
\rfoot{{{right_footer}}}
'''


def _generate_professional_title_page(layout_name: str, document_type: str = "report") -> str:
    """Generate professional LaTeX title page with logo support.
    
    Args:
        layout_name: Layout name to use
        document_type: Type of document ("report" or "paper")
        
    Returns:
        String containing LaTeX code for professional title page, or empty string for papers
    """
    # Papers use standard LaTeX title formatting, not custom title pages
    if document_type == "paper":
        return ""
    
    # Load project information with constitutional separation
    from ePy_docs.internals.styling._project_info import get_constitutional_project_info
    from ePy_docs.config.setup import get_setup_config
    
    try:
        # Use constitutional project info based on document type
        constitutional_info = get_constitutional_project_info(document_type)
        project_info = constitutional_info['project']  # Extract project section
        setup_config = get_setup_config()
    except Exception:
        constitutional_info = {'authors': [], 'project': {'name': 'Project Name', 'description': 'Project Description'}}
        project_info = constitutional_info['project']
        setup_config = {'copyright': {'year': '2025', 'holder': 'Author Name'}}
    
    # Extract title and author information from constitutional data
    title = project_info.get('name', 'Document Title')
    subtitle = project_info.get('description', '')
    
    # Get primary author from the authors array in constitutional info
    constitutional_authors = constitutional_info.get('authors', [])
    author = constitutional_authors[0]['name'] if constitutional_authors else 'Author Name'
    
    # Extract date and copyright info
    copyright_year = setup_config.get('copyright', {}).get('year', '2025')
    copyright_holder = setup_config.get('copyright', {}).get('holder', author)
    
    # Look for logo in brand folder
    logo_path = _find_logo_for_layout(layout_name)
    logo_latex = ""
    
    if logo_path:
        # For LaTeX, we need absolute paths to ensure the file can be found
        # regardless of the working directory where LaTeX is executed
        from pathlib import Path
        
        # Always use absolute path for LaTeX to avoid path resolution issues
        latex_logo_path = str(Path(logo_path).resolve()).replace('\\', '/')
        
        logo_latex = f"""
        \\begin{{center}}
        \\includegraphics[width=0.3\\textwidth]{{{latex_logo_path}}}
        \\end{{center}}
        \\vspace{{1cm}}"""
    
    # Generate professional title page LaTeX (only for reports)
    title_page_latex = f"""
% Professional Title Page (Reports only)
\\renewcommand{{\\maketitle}}{{
\\begin{{titlepage}}
\\centering
{logo_latex}

{{\\Huge\\bfseries {title} \\par}}
\\vspace{{0.5cm}}
{{\\Large {subtitle} \\par}}
\\vspace{{1.5cm}}
{{\\Large\\textit{{{author}}} \\par}}
\\vfill
{{\\large {copyright_year} \\par}}
{{\\normalsize © {copyright_holder} \\par}}
\\end{{titlepage}}
\\newpage
}}"""
    
    return title_page_latex


def _find_logo_for_layout(layout_name: str) -> Optional[Path]:
    """Find logo file for the specified layout using setup.json configuration.
    
    Args:
        layout_name: Name of the layout to find logo for
        
    Returns:
        Path to logo file if found and exists, None otherwise
    """
    from pathlib import Path
    from ePy_docs.internals.data_processing._data import _safe_get_nested
    from ePy_docs.config.setup import get_config_section
    
    # First, check if user has specified a logo_png in setup config
    try:
        setup_config = get_config_section('general')
        logo_path_config = _safe_get_nested(setup_config, ['styling', 'logo_png'])
        
        if logo_path_config:
            # User has explicitly configured a logo path
            logo_file = Path(logo_path_config)
            
            # Convert to absolute path if relative
            if not logo_file.is_absolute():
                logo_file = Path.cwd() / logo_file
                
            if logo_file.exists():
                return logo_file
            else:
                # User specified path but file doesn't exist - return None (no logo)
                return None
    
    except Exception:
        # If there's any error reading setup.json, fall back to auto-detection
        pass
    
    # Fallback: auto-detect logo in brand directory
    # Define possible logo file extensions
    logo_extensions = ['.png', '.jpg', '.jpeg', '.pdf', '.svg']
    
    # Check in data/user/brand/ directory
    brand_dir = Path.cwd() / 'data' / 'user' / 'brand'
    
    if brand_dir.exists():
        # Look for layout-specific logo first
        for ext in logo_extensions:
            logo_file = brand_dir / f"{layout_name}_logo{ext}"
            if logo_file.exists():
                return logo_file
        
        # Look for generic logo files
        for ext in logo_extensions:
            for generic_name in ['logo', 'brand', 'header']:
                logo_file = brand_dir / f"{generic_name}{ext}"
                if logo_file.exists():
                    return logo_file
    
    return None


class PDFRenderer:
    """Handles PDF rendering using Quarto with configuration from pages.json."""
    
    def __init__(self):
        """Initialize PDF renderer with styling configuration."""
        from ePy_docs.config.setup import _load_cached_config
        
        # Load PDF settings from pages.json using unified system
        page_config = _load_cached_config('page')
        if not page_config:
            raise ValueError("Missing page configuration from pages.json")
        
        # Get report configuration for layout information
        report_config = _load_cached_config('report')
        if not report_config:
            raise ValueError("Missing report configuration from report.json")
        
        try:
            # Get layout configuration for dynamic margins
            from ePy_docs.internals.styling._pages import get_current_layout
            layout_name = get_current_layout()
            if layout_name not in report_config['layouts']:
                raise ValueError(f"Layout '{layout_name}' not found in report.json")
            
            current_layout = report_config['layouts'][layout_name]
            layout_margins = current_layout['margins']
            
            # Convert inches to points for ReportLab (1 inch = 72 points)
            margin_top_pts = layout_margins['top'] * 72
            margin_bottom_pts = layout_margins['bottom'] * 72
            margin_left_pts = layout_margins['left'] * 72
            margin_right_pts = layout_margins['right'] * 72
            
            # Extract PDF-related settings from page config
            if 'toc' not in page_config:
                raise ValueError("Missing 'toc' in pages.json")
            if 'toc-depth' not in page_config:
                raise ValueError("Missing 'toc-depth' in pages.json")
            if 'number-sections' not in page_config:
                raise ValueError("Missing 'number-sections' in pages.json")
            
            # Get settings from format configuration
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
            
            # Store the current layout for color configuration
            self.layout = layout_name
            
        except Exception as e:
            raise ValueError(f"Error loading page configuration: {e}")
    
    def _load_crossref_config(self) -> Dict[str, Any]:
        """Load crossref configuration from component JSON files."""
        from ePy_docs.config.setup import _load_cached_config
        crossref_config = {}
        
        # Load images crossref (figures) - REQUIRED
        images_config = _load_cached_config('images')
        if not images_config or 'crossref' not in images_config:
            raise ValueError("Missing 'crossref' configuration in images.json")
        crossref_config.update(images_config['crossref'])
        
        # Load tables crossref - REQUIRED
        tables_config = _load_cached_config('tables')
        if not tables_config or 'crossref' not in tables_config:
            raise ValueError("Missing 'crossref' configuration in tables.json")
        crossref_config.update(tables_config['crossref'])
        
        # Load equations crossref - REQUIRED
        equations_config = _load_cached_config('equations')
        if not equations_config or 'crossref' not in equations_config:
            raise ValueError("Missing 'crossref' configuration in equations.json")
        crossref_config.update(equations_config['crossref'])
        
        return crossref_config
    
    def _load_typography_config(self, header_style: str = "formal") -> Dict[str, Any]:
        """Load typography configuration from JSON files - NO FALLBACKS.
        
        Args:
            header_style: The header style to use ('formal', 'modern', 'branded', 'clean').
            sync_files: If True, forces reload from disk and updates cache.
        """
        from ePy_docs.config.setup import _load_cached_config
        
        # Load text configuration - REQUIRED
        text_config = _load_cached_config('text')
        if not text_config:
            raise ValueError("Missing text configuration from text.json")
        
        #  PURIFICADO: Load colors through guardian - NO DIRECT ACCESS!
        from ePy_docs.internals.styling._colors import get_colors_config
        try:
            colors_config = get_colors_config()
        except Exception as e:
            raise ValueError(f"Failed to load colors configuration: {e}. Please ensure colors.json is properly configured.")
        
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
        if 'layout_styles' not in colors_config['reports']:
            raise ValueError("Missing 'layout_styles' section in colors configuration")
        layout_styles = colors_config['reports']['layout_styles']
        if not layout_styles:
            raise ValueError("Missing 'layout_styles' section in colors configuration")
        if header_style not in layout_styles:
            raise ValueError(f"Layout style '{header_style}' not found in colors configuration")
        
        text_colors = layout_styles[header_style]
        
        # Process styles - NO DEFAULTS
        combined_styles = {}
        
        # Process headers (h1, h2, h3, h4, h5, h6) - REQUIRED
        for header_key in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            if header_key not in headers_config:
                raise ValueError(f"Missing '{header_key}' configuration in components/text.json headers")
            
            combined_styles[header_key] = headers_config[header_key].copy()
            
            if header_key not in text_colors:
                raise ValueError(f"Missing '{header_key}' color configuration in colors.json")
            combined_styles[header_key]['textColor'] = text_colors[header_key]
        
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
        """Create PDF-specific YAML configuration using current layout colors.
        
        Args:
            title: Document title
            author: Document author
            header_style: The header style to use ('formal', 'modern', 'branded', 'clean').
            
        Returns:
            PDF configuration dictionary
        """
        margins = self.pdf_settings['margins']
        pagesize = self.pdf_settings['pagesize']
        
        # Load typography configuration using current layout
        styles = self._load_typography_config(header_style=self.layout)
        
        # Convert margins from points to inches
        margin_top = margins['top'] / 72
        margin_bottom = margins['bottom'] / 72
        margin_left = margins['left'] / 72
        margin_right = margins['right'] / 72
        
        h1 = styles['h1']
        h2 = styles['h2'] 
        h3 = styles['h3']
        h4 = styles['h4']
        h5 = styles['h5']
        h6 = styles['h6']
        normal = styles['normal']
        
        # Convert RGB colors to hex format
        def rgb_to_hex(rgb_list):
            return f"#{rgb_list[0]:02x}{rgb_list[1]:02x}{rgb_list[2]:02x}"
        
        h1_color = rgb_to_hex(h1['textColor'])
        h2_color = rgb_to_hex(h2['textColor'])
        h3_color = rgb_to_hex(h3['textColor'])
        h4_color = rgb_to_hex(h4['textColor'])
        h5_color = rgb_to_hex(h5['textColor'])
        h6_color = rgb_to_hex(h6['textColor'])
        normal_color = rgb_to_hex(normal['textColor'])  # Add normal text color
        
        # Create LaTeX header for custom styling and figure handling as a list
        latex_header = [
            "\\usepackage{xcolor}",
            "\\usepackage{float}",
            "\\usepackage{caption}",
            "\\usepackage{subcaption}",
            f"\\definecolor{{h1color}}{{HTML}}{{{h1_color[1:]}}}",
            f"\\definecolor{{h2color}}{{HTML}}{{{h2_color[1:]}}}",
            f"\\definecolor{{h3color}}{{HTML}}{{{h3_color[1:]}}}",
            f"\\definecolor{{h4color}}{{HTML}}{{{h4_color[1:]}}}",
            f"\\definecolor{{h5color}}{{HTML}}{{{h5_color[1:]}}}",
            f"\\definecolor{{h6color}}{{HTML}}{{{h6_color[1:]}}}",
            f"\\definecolor{{normalcolor}}{{HTML}}{{{normal_color[1:]}}}",  # Define normal text color
            "\\makeatletter",
            f"\\renewcommand{{\\section}}{{\\@startsection{{section}}{{1}}{{\\z@}}{{{h1['spaceBefore']}pt}}{{{h1['spaceAfter']}pt}}{{\\normalfont\\fontsize{{{h1['fontSize']}}}{{{h1['leading']}}}\\selectfont\\bfseries\\color{{h1color}}}}}}",
            f"\\renewcommand{{\\subsection}}{{\\@startsection{{subsection}}{{2}}{{\\z@}}{{{h2['spaceBefore']}pt}}{{{h2['spaceAfter']}pt}}{{\\normalfont\\fontsize{{{h2['fontSize']}}}{{{h2['leading']}}}\\selectfont\\bfseries\\color{{h2color}}}}}}",
            f"\\renewcommand{{\\subsubsection}}{{\\@startsection{{subsubsection}}{{3}}{{\\z@}}{{{h3['spaceBefore']}pt}}{{{h3['spaceAfter']}pt}}{{\\normalfont\\fontsize{{{h3['fontSize']}}}{{{h3['leading']}}}\\selectfont\\bfseries\\color{{h3color}}}}}}",
            f"\\renewcommand{{\\paragraph}}{{\\@startsection{{paragraph}}{{4}}{{\\z@}}{{{h4['spaceBefore']}pt}}{{{h4['spaceAfter']}pt}}{{\\normalfont\\fontsize{{{h4['fontSize']}}}{{{h4['leading']}}}\\selectfont\\bfseries\\color{{h4color}}}}}}",
            f"\\renewcommand{{\\subparagraph}}{{\\@startsection{{subparagraph}}{{5}}{{\\z@}}{{{h5['spaceBefore']}pt}}{{{h5['spaceAfter']}pt}}{{\\normalfont\\fontsize{{{h5['fontSize']}}}{{{h5['leading']}}}\\selectfont\\bfseries\\color{{h5color}}}}}}",
            # H6 doesn't have a direct LaTeX equivalent, so we'll create a custom command
            f"\\newcommand{{\\heading6}}[1]{{\\vspace{{{h6['spaceBefore']}pt}}{{\\fontsize{{{h6['fontSize']}}}{{{h6['leading']}}}\\selectfont\\bfseries\\color{{h6color}}#1}}\\vspace{{{h6['spaceAfter']}pt}}}}",
            "\\makeatother",
            "\\color{normalcolor}",  # Set default text color for entire document
            "\\captionsetup[figure]{position=bottom,labelfont=bf,textfont=normal}",
            "\\floatplacement{figure}{H}"
        ]
        
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
                    # Add link colors automatically from brand_primary if available
                    **{k: v for k, v in self.pdf_settings.items() if k in ['linkcolor', 'urlcolor', 'citecolor', 'anchorcolor']},
                    'fontsize': f"{normal['fontSize']}pt",
                    'header-includes': latex_header,
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


def _get_font_latex_config(font_family: str) -> str:
    """Generate LaTeX font configuration based on font family from text.json.
    
    Args:
        font_family: Font family name from text.json
        sync_files: Whether to sync configuration files
        
    Returns:
        LaTeX commands for font configuration
    """
    from ePy_docs.config.setup import get_config_section
    
    try:
        text_config = get_config_section('text')
    except Exception:
        text_config = {}
    
    if 'latex_fonts' not in text_config:
        raise ValueError("latex_fonts configuration not found in text config")
    
    latex_fonts = text_config['latex_fonts']
    
    if font_family not in latex_fonts:
        raise ValueError(f"Font family '{font_family}' not found in text.json latex_fonts")
    
    font_config = latex_fonts[font_family]
    
    if 'package' not in font_config:
        raise ValueError(f"package not found for font '{font_family}' in latex_fonts")
    if 'command' not in font_config:
        raise ValueError(f"command not found for font '{font_family}' in latex_fonts")
    
    return f"\\usepackage{{{font_config['package']}}}\n{font_config['command']}"


def _get_callout_pagebreak_latex_config() -> str:
    """Generate LaTeX configuration for callout page break control from notes.json.
    
    Returns:
        LaTeX commands for callout page break configuration
    """
    from ePy_docs.config.setup import get_config_section
    
    try:
        notes_config = get_config_section('notes')
    except Exception:
        notes_config = {}
    
    if 'callout_pagebreak' not in notes_config:
        return ""
    
    pagebreak_config = notes_config['callout_pagebreak']
    penalty_value = pagebreak_config.get('penalty', -100)
    
    return f'''
% Callout page break control
\\widowpenalty={penalty_value}
\\clubpenalty={penalty_value}
'''
