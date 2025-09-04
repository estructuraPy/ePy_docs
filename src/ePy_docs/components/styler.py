"""Quarto Document Generation and Styling for ePy_docs.

This module handles document generation using Quarto, including PDF and HTML
output formats. It provides functions to create Quarto YAML configurations,
generate CSS styles, and set up complete Quarto projects for document compilation.
"""
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
import os
import yaml
import shutil
import subprocess
import json

# Import from the page configuration module
from ePy_docs.components.pages import (
    get_project_config, get_config_value, _ConfigManager,
    get_layout_config, get_header_style, validate_csl_style,
    sync_ref, create_css_styles
)

def rgb_to_latex_str(rgb_values: List[int]) -> str:
    """Convert RGB values to LaTeX color string format.
    
    Args:
        rgb_values: List of 3 integers representing RGB values [R, G, B]
        
    Returns:
        String in format "R,G,B" for LaTeX \definecolor commands
        
    Example:
        rgb_to_latex_str([255, 0, 0]) -> "255,0,0"
    """
    if not isinstance(rgb_values, list) or len(rgb_values) != 3:
        raise ValueError(f"RGB values must be a list of 3 integers, got: {rgb_values}")
    
    # Ensure values are integers and within valid range
    rgb_ints = []
    for val in rgb_values:
        if not isinstance(val, (int, float)):
            raise ValueError(f"RGB values must be numbers, got: {type(val)}")
        rgb_int = int(val)
        if rgb_int < 0 or rgb_int > 255:
            raise ValueError(f"RGB values must be between 0-255, got: {rgb_int}")
        rgb_ints.append(rgb_int)
    
    return f"{rgb_ints[0]},{rgb_ints[1]},{rgb_ints[2]}"
from ePy_docs.components.references import get_default_citation_style
from ePy_docs.components.colors import get_colors_config
# Note: removed generate_latex_callout_config - now using image-based notes

def _load_config_file(config_type: str = "page", sync_files: bool = None) -> Dict[str, Any]:
    """Load configuration file using ConfigManager.
    
    Args:
        config_type: Type of configuration to load ('page' or 'report')
        sync_files: Whether to sync configuration files
        
    Returns:
        Dict containing the configuration
    """
    valid_types = ["page", "report"]
    if config_type not in valid_types:
        raise ValueError(f"Invalid config_type '{config_type}'. Must be one of: {valid_types}")
    
    from ePy_docs.components.pages import _ConfigManager
    from ePy_docs.components.setup import get_current_project_config
    from ePy_docs.files.data import clear_local_config_cache
    
    current_config = get_current_project_config()
    if current_config is None:
        raise ValueError("No project configuration found.")
        
    from ePy_docs.components.setup import _load_cached_files, _resolve_config_path
    
    try:
        # Handle special case for 'page' -> 'pages'
        actual_config_type = 'pages' if config_type == 'page' else config_type
        config_path = _resolve_config_path(actual_config_type, sync_files=sync_files)
        config = _load_cached_files(config_path, sync_files=sync_files)
    except Exception:
        config = {}
    
    if not config:
        raise ValueError(f"Configuration file not found: components/{config_type}.json")
        
    return config

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

def generate_quarto_config(layout_name: str = None, sync_files: bool = None) -> Dict[str, Any]:
    """Generate Quarto YAML configuration from project settings.
    
    Args:
        layout_name: Layout name to use. If None, uses global current layout.
        sync_files: Whether to sync configuration files. If None, uses project setting.
        
    Returns:
        Dict[str, Any]: Complete Quarto YAML configuration dictionary.
    """
    # Determine sync_files setting if not provided
    if sync_files is None:
        from ePy_docs.components.setup import get_current_project_config
        current_config = get_current_project_config()
        sync_files = current_config.settings.sync_files if current_config else False
    
    # Load configuration from pages.json - respecting sync_files parameter
    page_config = _load_config_file("page", sync_files=sync_files)
    
    # Get layout configuration from report.json - ALWAYS load report_config
    report_config = _load_config_file("report", sync_files=sync_files)
    
    # Determine layout_name if not provided
    if layout_name is None:
        from ePy_docs.components.pages import get_current_layout
        layout_name = get_current_layout()
    
    # Load project configuration
    project_config = get_project_config()
    
    # Extract relevant project information - NO FALLBACKS
    project_info = project_config['project']
    copyright_info = project_config['copyright']
    
    # Get document information - all from JSON, fail if missing
    title = project_info['name']
    subtitle = project_info['description']
    author_date = project_info['created_date']
    
    # Get header style from layout
    header_style_from_layout = get_header_style(layout_name)
    
    # Determine CSL style from layout
    citation_style = get_default_citation_style(layout_name)
    csl_file = validate_csl_style(citation_style, sync_files=sync_files)
    
    # Get bibliography configuration using our new function that respects sync_files
    from ePy_docs.components.references import get_bibliography_config
    from ePy_docs.components.setup import get_current_project_config
    from pathlib import Path
    
    dir_config = get_current_project_config()
    if dir_config is None:
        raise ValueError("No project configuration found.")
        
    bib_config = get_bibliography_config(config=dir_config, sync_files=sync_files)
    bib_path = str(bib_config['bibliography']).replace("\\", "/")
    csl_path = str(bib_config['csl']).replace("\\", "/")
    
    styler_config = page_config
    
    # Get crossref configuration from component JSON files, NO FALLBACKS
    from ePy_docs.components.setup import _load_cached_files, _resolve_config_path
    
    # Load configuration for images (for display settings, not crossref)
    try:
        config_path = _resolve_config_path('images', sync_files=sync_files)
        images_full_config = _load_cached_files(config_path, sync_files=sync_files)
        
        # Get layout-specific images configuration from layout manager
        from ePy_docs.components.layout import LayoutManager
        layout_manager = LayoutManager()
        layout_config = layout_manager.get_layout_config(layout_name)
        images_config = layout_config.get('images', {})
        
        # If no layout-specific config, fallback to display settings from main config
        if not images_config or 'display' not in images_config:
            images_config = {
                'display': images_full_config.get('display', {}),
                'styling': {'alignment': 'center'}  # Default alignment
            }
    except Exception:
        images_config = {
            'display': {'max_width_inches_html': 7, 'max_width_inches': 6.5, 'dpi': 300, 'html_responsive': True},
            'styling': {'alignment': 'center'}
        }
    
    if not images_config:
        raise ValueError("Missing images configuration in components/images.json")
    
    # Load font configuration from text.json using unified system - NO FALLBACKS
    try:
        config_path = _resolve_config_path('text', sync_files=sync_files)
        text_config = _load_cached_files(config_path, sync_files=sync_files)
    except Exception:
        text_config = {}
    if not text_config:
        raise ValueError("Missing text configuration from components/text.json")
    
    # Get text style configuration based on layout name (header_style_from_layout now returns layout name)
    if 'layout_styles' not in text_config:
        raise ValueError("Missing layout_styles configuration in text.json")
    
    layout_name = header_style_from_layout  # This is now the layout name due to unified system
    if layout_name not in text_config['layout_styles']:
        available_layouts = ', '.join(text_config['layout_styles'].keys())
        raise ValueError(f"Layout '{layout_name}' not found in text.json. Available layouts: {available_layouts}")
    
    layout_config = text_config['layout_styles'][layout_name]
    
    if 'typography' not in layout_config or 'normal' not in layout_config['typography']:
        raise ValueError(f"Missing typography.normal configuration for layout '{layout_name}' in text.json")
    
    normal_text = layout_config['typography']['normal']
    if 'size' not in normal_text:
        raise ValueError("Missing size in typography.normal configuration")
    if 'family' not in normal_text:
        raise ValueError("Missing family in typography.normal configuration")
    
    font_size = normal_text['size']
    font_family = normal_text['family']
    # Default line spacing since it's not in current text.json structure
    line_spacing = 1.5
    
    # Get margins from current layout from report.json instead of pages.json
    if layout_name not in report_config['layouts']:
        raise ValueError(f"Layout '{layout_name}' not found in report.json")
    
    current_layout = report_config['layouts'][layout_name]
    layout_margins = current_layout['margins']
    
    # Convert inches to mm for LaTeX (1 inch = 25.4 mm)
    margin_top_mm = f"{layout_margins['top'] * 25.4:.0f}mm"
    margin_bottom_mm = f"{layout_margins['bottom'] * 25.4:.0f}mm"
    margin_left_mm = f"{layout_margins['left'] * 25.4:.0f}mm"
    margin_right_mm = f"{layout_margins['right'] * 25.4:.0f}mm"
    
    config = {
        'project': {
            'type': report_config['project']['type']
        },
        'lang': report_config['project']['lang'],
        'book': {
            'title': title,
            'subtitle': subtitle,
            'author': author_date,
        },
        'bibliography': bib_path,
        'csl': csl_path,
        'execute': {
            'echo': page_config['execute']['echo']
        },
        'crossref': {
            'chapters': page_config['crossref']['chapters'],
            'eq-labels': page_config['crossref']['eq-labels'],
            'fig-labels': page_config['crossref']['fig-labels'],
            'tbl-labels': page_config['crossref']['tbl-labels']
        }
    }
    
    # Get colors for styling based on layout name (header_style_from_layout is now layout name)
    # Get header colors based on the layout's unified layout_styles
    layout_name = header_style_from_layout  # This is now the layout name
    h1_color_rgb = get_color(f'layout_styles.{layout_name}.typography.h1', format_type="rgb")
    h2_color_rgb = get_color(f'layout_styles.{layout_name}.typography.h2', format_type="rgb")
    h3_color_rgb = get_color(f'layout_styles.{layout_name}.typography.h3', format_type="rgb")
    h4_color_rgb = get_color(f'layout_styles.{layout_name}.typography.h4', format_type="rgb")
    h5_color_rgb = get_color(f'layout_styles.{layout_name}.typography.h5', format_type="rgb")
    h6_color_rgb = get_color(f'layout_styles.{layout_name}.typography.h6', format_type="rgb")
    normal_color_rgb = get_color(f'layout_styles.{layout_name}.typography.normal', format_type="rgb")
    
    # Get header and footer colors from layout_styles
    header_color_rgb = get_color(f'layout_styles.{layout_name}.typography.header_color', format_type="rgb")
    footer_color_rgb = get_color(f'layout_styles.{layout_name}.typography.footer_color', format_type="rgb")
    page_number_color_rgb = get_color(f'layout_styles.{layout_name}.typography.page_number_color', format_type="rgb")
    
    # Get background color for the layout
    try:
        background_color_rgb = get_color(f'layout_styles.{layout_name}.typography.background_color', format_type="rgb")
    except Exception:
        # Fallback to white background if not defined
        background_color_rgb = [255, 255, 255]
    
    # Also get brand colors for other elements
    primary_blue = get_color('brand.secondary', format_type="hex")
    accent_red = get_color('brand.primary', format_type="hex")
    secondary_gray = get_color('brand.tertiary', format_type="hex")
    
    # Gray scales - all from config
    gray_1 = get_color('grays_cool.light', format_type="hex")
    gray_2 = get_color('grays_cool.medium', format_type="hex")
    gray_4 = get_color('grays_cool.dark', format_type="hex")
    
    # Get page layout configuration for header/footer generation
    page_layout_config = None
    if 'page_layout_key' in current_layout:
        page_layout_key = current_layout['page_layout_key']
        if 'layouts' in page_config and page_layout_key in page_config['layouts']:
            page_layout_config = page_config['layouts'][page_layout_key]
    
    # Generate dynamic header/footer LaTeX based on layout configuration
    header_footer_latex = _generate_header_footer_latex(
        page_layout_config, 
        project_config, 
        copyright_info, 
        layout_name
    )
    if 'common' not in styler_config['format']:
        raise ValueError("Missing 'common' section in format configuration")
    if 'pdf' not in styler_config['format']:
        raise ValueError("Missing 'pdf' section in format configuration")
        
    common_config = styler_config['format']['common']
    pdf_format_config = styler_config['format']['pdf']
    
    # Merge common and PDF-specific configurations
    merged_pdf_config = {**common_config, **pdf_format_config}
    
    pdf_config = {
        'number-sections': merged_pdf_config['number-sections'],
        # APLICAR MÁRGENES DEL LAYOUT - Esta era la configuración faltante
        'geometry': [
            f"top={margin_top_mm}",
            f"bottom={margin_bottom_mm}",
            f"left={margin_left_mm}",
            f"right={margin_right_mm}"
        ],
        'include-in-header': {
            'text': rf'''
\usepackage[utf8]{{inputenc}}

\usepackage{{fontenc}}
\usepackage{{lmodern}}
{_get_font_latex_config(font_family, sync_files=sync_files)}

\usepackage{{xcolor}}
\definecolor{{pagebackground}}{{RGB}}{{{rgb_to_latex_str(background_color_rgb)}}}
\usepackage{{pagecolor}}
\pagecolor{{pagebackground}}

\usepackage{{fancyhdr}}
\pagestyle{{fancy}}

\clearpage
\setcounter{{page}}{{0}}
\pagenumbering{{arabic}}

{header_footer_latex}

\usepackage{{graphicx}}

\definecolor{{brandSecondary}}{{RGB}}{{{rgb_to_latex_str(get_color('brand.secondary', format_type="rgb"))}}}
\definecolor{{Gray_1}}{{RGB}}{{{rgb_to_latex_str(get_color('grays_cool.light', format_type="rgb"))}}}
\definecolor{{Gray_2}}{{RGB}}{{{rgb_to_latex_str(get_color('grays_cool.medium', format_type="rgb"))}}}
\definecolor{{Gray_4}}{{RGB}}{{{rgb_to_latex_str(get_color('grays_cool.dark', format_type="rgb"))}}}

\definecolor{{h1color}}{{RGB}}{{{rgb_to_latex_str(h1_color_rgb)}}}
\definecolor{{h2color}}{{RGB}}{{{rgb_to_latex_str(h2_color_rgb)}}}
\definecolor{{h3color}}{{RGB}}{{{rgb_to_latex_str(h3_color_rgb)}}}
\definecolor{{h4color}}{{RGB}}{{{rgb_to_latex_str(h4_color_rgb)}}}
\definecolor{{h5color}}{{RGB}}{{{rgb_to_latex_str(h5_color_rgb)}}}
\definecolor{{h6color}}{{RGB}}{{{rgb_to_latex_str(h6_color_rgb)}}}
\definecolor{{normalcolor}}{{RGB}}{{{rgb_to_latex_str(normal_color_rgb)}}}

\definecolor{{headercolor}}{{RGB}}{{{rgb_to_latex_str(header_color_rgb)}}}
\definecolor{{footercolor}}{{RGB}}{{{rgb_to_latex_str(footer_color_rgb)}}}
\definecolor{{pagenumbercolor}}{{RGB}}{{{rgb_to_latex_str(page_number_color_rgb)}}}

% Callout page break control configuration from notes.json
{_get_callout_pagebreak_latex_config(sync_files=sync_files)}

\usepackage{{amsmath}}
\usepackage{{amssymb}}
\usepackage{{amsfonts}}
\usepackage{{sectsty}}
\chapterfont{{\color{{h1color}}}}
\sectionfont{{\color{{h2color}}}}
\subsectionfont{{\color{{h3color}}}}
\subsubsectionfont{{\color{{h4color}}}}
\paragraphfont{{\color{{h5color}}}}
\subparagraphfont{{\color{{h6color}}}}

\color{{normalcolor}}
\color{{normalcolor}}

\makeatletter
\renewcommand{{\paragraph}}{{\@startsection{{paragraph}}{{4}}{{\z@}}{{3.25ex \@plus1ex \@minus.2ex}}{{-1em}}{{\normalfont\normalsize\bfseries\color{{h4color}}}}}}
\renewcommand{{\subparagraph}}{{\@startsection{{subparagraph}}{{5}}{{\parindent}}{{3.25ex \@plus1ex \@minus .2ex}}{{-1em}}{{\normalfont\normalsize\bfseries\color{{h5color}}}}}}
\newcommand{{\headingsix}}[1]{{%
    \vspace{{2ex}}%
    {{\normalfont\small\bfseries\color{{h6color}}##1}}%
    \vspace{{1ex}}%
}}
\makeatother

\newenvironment{{contentblock}}
  {{\begin{{minipage}}{{\textwidth}}}}
  {{\end{{minipage}}\par\vspace{{\baselineskip}}}}

\newenvironment{{content-block}}{{\begin{{contentblock}}}}{{\end{{contentblock}}}}

\makeatletter
\def\thickhrulefill{{\leavevmode \leaders \hrule height 1pt\hfill \kern \z@}}
\renewcommand{{\maketitle}}{{\begin{{titlepage}}%
  \let\footnotesize\small
  \let\footnoterule\relax
  \parindent \z@
  \reset@font
  \null
  \vskip 10\p@
  \hbox{{\mbox{{\hspace{{3em}}}}%
    \vrule depth 0.6\textheight %
    \mbox{{\hspace{{2em}}}}
    \vbox{{
      \vskip 40\p@
      \begin{{flushleft}}
        \Large \@author \par
      \end{{flushleft}}
      \vskip 80\p@
      \begin{{flushleft}}
        \huge \bfseries \@title \par
      \end{{flushleft}}
      \vfill
      }}}}
    \null
  \end{{titlepage}}%
  \setcounter{{footnote}}{{0}}%
}} 
\makeatother
'''
        },
        'documentclass': merged_pdf_config['documentclass'],
        'fontsize': f'{font_size}pt',
        'papersize': merged_pdf_config['papersize'],
        # Margins are already configured via geometry above - removing duplicate hardcoded values
        'linestretch': line_spacing,
        'toc-depth': merged_pdf_config['toc-depth'],
        'toc': merged_pdf_config['toc'],
        'lof': merged_pdf_config['lof'],
        'lot': merged_pdf_config['lot'],
        # Figure configurations from images.json
        'fig-width': images_config.get('display', {}).get('max_width_inches', 6.5),
        'fig-height': images_config.get('display', {}).get('max_width_inches', 6.5) * 0.65,  # Maintain aspect ratio
        'fig-pos': merged_pdf_config['fig-pos'],
        'fig-cap-location': merged_pdf_config['fig-cap-location'],
        'colorlinks': merged_pdf_config.get('colorlinks', False)
    }
    
    # Create HTML format configuration - NO FALLBACKS, read from component configs
    if 'html' not in styler_config['format']:
        raise ValueError("Missing 'html' section in format configuration")
    
    html_format_config = styler_config['format']['html']
    
    # Merge common and HTML-specific configurations
    merged_html_config = {**common_config, **html_format_config}
    
    html_config = {
        'theme': merged_html_config['theme'],
        'css': 'styles.css',  # Add CSS reference
        'toc': merged_html_config['toc'],
        'toc-depth': merged_html_config['toc-depth'],
        'number-sections': merged_html_config['number-sections'],
        'html-math-method': 'mathjax',
        'self-contained': merged_html_config['self-contained'],
        'embed-resources': merged_html_config['embed-resources'],
        # Figure configurations from images.json
        'fig-width': images_config.get('display', {}).get('max_width_inches_html', 7),
        'fig-height': images_config.get('display', {}).get('max_width_inches_html', 7) * 0.6,  # Maintain aspect ratio
        'fig-align': images_config.get('styling', {}).get('alignment', 'center').lower(),
        'fig-responsive': images_config.get('display', {}).get('html_responsive', True),
        'fig-cap-location': merged_html_config['fig-cap-location'],
        'tbl-cap-location': merged_html_config['tbl-cap-location'],
        'fig-dpi': images_config.get('display', {}).get('dpi', 300) // 2,  # Half DPI for HTML
        'code-fold': merged_html_config['code-fold'],
        'code-tools': merged_html_config['code-tools']
    }
    
    # Add format configurations to main config
    config['format'] = {
        'pdf': pdf_config,
        'html': html_config
    }
    
    return config

def create_quarto_yml(output_dir: str, chapters: Optional[List[str]] = None) -> str:
    """Create _quarto.yml file from project configuration.
    
    Args:
        output_dir: Directory where the _quarto.yml file will be created.
        chapters: Optional list of chapter paths to include in the configuration.
        
    Returns:
        str: Absolute path to the created _quarto.yml file.
    """
    config = generate_quarto_config()
    
    if chapters:
        config['book']['chapters'] = chapters
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    config_file = output_path / "_quarto.yml"
    try:
        from ePy_docs.api.file_management import write_text
        import yaml
        yaml_content = yaml.dump(config, default_flow_style=False, sort_keys=False, allow_unicode=True)
        write_text(yaml_content, config_file)
    except Exception as e:
        raise RuntimeError(f"Failed to write Quarto configuration file: {e}")
    
    css_file = output_path / "styles.css"
    from ePy_docs.components.pages import get_current_layout
    current_layout = get_current_layout()
    css_content = create_css_styles(layout_name=current_layout)
    try:
        from ePy_docs.api.file_management import write_text
        write_text(css_content, css_file)
    except Exception as e:
        raise RuntimeError(f"Failed to write CSS file: {e}")
    
    return str(config_file)

def create_quarto_project(output_dir: str, 
                         chapters: Optional[List[str]] = None, 
                         sync_files: bool = True,
                         create_index: bool = True) -> Dict[str, str]:
    """Create a complete Quarto project directory with all necessary files.
    
    This function creates a ready-to-compile Quarto book project with:
    - _quarto.yml configuration file
    - styles.css for HTML output styling  
    
    Citation style is automatically determined from the layout in pages.json.  
    - index.qmd (optional) as the main entry point
    - All necessary configuration based on project JSON files
    
    Args:
        output_dir: Directory where the Quarto project will be created.
        citation_style: Citation style to use. If not provided, uses layout default.
        chapters: Optional list of chapter paths to include. If provided,
            these will be set as the book chapters in order.
        sync_files: Whether to synchronize JSON files before reading. Defaults to True.
        create_index: Whether to create an index.qmd file. Defaults to True.
        layout_name: Layout to use for default settings. Defaults to 'technical'.
        
    Returns:
        Dict[str, str]: Dictionary with paths to created files:
            - 'quarto_yml': Path to _quarto.yml
            - 'styles_css': Path to styles.css  
            - 'index_qmd': Path to index.qmd (if created)
            - 'project_dir': Path to the project directory
        
    Raises:
        ValueError: If citation_style is not supported.
        OSError: If output_dir cannot be created or is not writable.
        
    Example:
        >>> files = create_quarto_project("/path/to/my_book", 
        ...                              chapters=["intro.qmd", "chapter1.qmd"])
        >>> print(f"Project created at: {files['project_dir']}")
    """
    # Validation will be handled by generate_quarto_config() when citation_style is used
    
    # Create the output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    created_files = {}
    created_files['project_dir'] = str(output_path.absolute())
    
    # 1. Create _quarto.yml configuration - citation style determined automatically
    quarto_yml_path = create_quarto_yml(
        output_dir=output_dir,
        chapters=chapters,
        sync_files=sync_files
    )
    created_files['quarto_yml'] = quarto_yml_path
    
    # 2. CSS file is already created by create_quarto_yml
    css_path = output_path / "styles.css"
    created_files['styles_css'] = str(css_path.absolute())
    
    # 3. Create index.qmd if requested
    if create_index:
        index_content = create_index_qmd(sync_files=sync_files)
        index_path = output_path / "index.qmd"
        
        try:
            from ePy_docs.api.file_management import write_text
            write_text(index_content, index_path)
        except Exception as e:
            raise RuntimeError(f"Failed to write index.qmd file: {e}")
        
        created_files['index_qmd'] = str(index_path.absolute())
    
    return created_files

def create_index_qmd() -> str:
    """Create content for an index.qmd file based on project configuration.
    
    Args:
        sync_files: Whether to synchronize JSON files before reading.
        
    Returns:
        str: Complete content for index.qmd file.
        
    Raises:
        FileNotFoundError: If project.json file doesn't exist.
        KeyError: If required keys are missing from configuration.
        JSONDecodeError: If JSON file is malformed.
    """
    from ePy_docs.components.setup import _load_cached_config
    
    # Read project configuration using unified system
    project_data = _load_cached_config('project_info')
    
    if not project_data:
        raise ValueError("Missing project configuration from project_info.json")
    
    # Extract project information - fail if missing
    project_info = project_data['project']
    title = project_info['name']
    description = project_info['description']
    version = project_info['version']
    code = project_info['code']
    created_date = project_info['created_date']
    
    # Extract consultant information - fail if missing
    consultants = project_data['consultants']
    author = consultants[0]['name']
    author_specialty = consultants[0]['specialty']
    author_license = consultants[0]['license']
    
    # Extract client information - fail if missing  
    client_info = project_data['client']
    client_name = client_info['name']
    
    # Extract location information - fail if missing
    location_info = project_data['location']
    location = f"{location_info['city']}, {location_info['country']}"
    
    # Build author description
    author_description = author
    author_details = []
    if author_license:
        author_details.append(f"Carné CFIA: {author_license}")
    if author_specialty:
        author_details.append(author_specialty)
    if author_details:
        author_description += f"  \n{' | '.join(author_details)}"
    
    index_content = f'''# Prefacio {{.unnumbered}}

Este documento presenta el proyecto "{title}".

**Descripción:** {description}

**Cliente:** {client_name}

**Ubicación:** {location}

## Información del Proyecto {{.unnumbered}}

- **Código:** {code}
- **Versión:** {version}
- **Fecha de creación:** {created_date}

## Acerca de este documento {{.unnumbered}}

Esta documentación ha sido generada utilizando ePy_docs, un sistema de documentación 
técnica que integra código, análisis y reportes de ingeniería estructural.

## Responsabilidad Profesional {{.unnumbered}}

**{author_description}**

---

*Generado con ePy_docs - Sistema de documentación técnica para ingeniería*
'''
    
    return index_content

# def copy_setup_files(setup_dir: str, sync_files: bool = True) -> None:
#     """Copy setup files including Word templates and other assets for Quarto.
    
#     This function ensures that necessary setup files (Word templates, logos, etc.)
#     exist in the specified setup directory. It will copy them from the package's
#     setup files if available.
    
#     Args:
#         setup_dir: Path to setup directory where files should be copied to.
#         sync_files: Whether to sync JSON files before looking for setup files.
#             Defaults to True.
            
#     Returns:
#         None
        
#     Assumes:
#         The setup_dir is writable. If the source setup directory doesn't exist
#         in the package, no files will be copied.
#     """
#     # Create setup directory if it doesn't exist
#     os.makedirs(setup_dir, exist_ok=True)
    
#     # Path to source setup files in package
#     src_setup_dir = Path(__file__).parent.parent / "setup"
    
#     # Only try to copy files if the source directory exists
#     if not src_setup_dir.exists():
#         # No setup files available to copy
#         return
    
#     # Copy Word template if available
#     template_file = os.path.join(setup_dir, "Template.docx")
#     src_template_file = src_setup_dir / "Template.docx"
    
#     if src_template_file.exists():
#         shutil.copy2(src_template_file, template_file)
    
#     # Copy logo files if available
#     logo_file = os.path.join(setup_dir, "logo.png")
#     src_logo_file = src_setup_dir / "logo.png"
    
#     if src_logo_file.exists():
#         shutil.copy2(src_logo_file, logo_file)
    
#     # Copy any other setup files
#     for file_path in src_setup_dir.iterdir():
#         if file_path.is_file() and file_path.name not in ["Template.docx", "logo.png"]:
#             dest_file = os.path.join(setup_dir, file_path.name)
#             try:
#                 shutil.copy2(file_path, dest_file)
#             except Exception:
#                 # Skip files that can't be copied
#                 pass

class PDFRenderer:
    """Handles PDF rendering using Quarto with configuration from pages.json."""
    
    def __init__(self):
        """Initialize PDF renderer with styling configuration."""
        from ePy_docs.components.setup import _load_cached_config
        
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
            from ePy_docs.components.pages import get_current_layout
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
        from ePy_docs.components.setup import _load_cached_config
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
    
    def _load_typography_config(self, header_style: str = "formal", sync_files: bool = False) -> Dict[str, Any]:
        """Load typography configuration from JSON files - NO FALLBACKS.
        
        Args:
            header_style: The header style to use ('formal', 'modern', 'branded', 'clean').
            sync_files: If True, forces reload from disk and updates cache.
        """
        from ePy_docs.components.setup import _load_cached_config
        
        # Load text configuration - REQUIRED
        text_config = _load_cached_config('text')
        if not text_config:
            raise ValueError("Missing text configuration from text.json")
        
        #  PURIFICADO: Load colors through guardian - NO DIRECT ACCESS!
        from ePy_docs.components.colors import get_colors_config
        try:
            colors_config = get_colors_config(sync_files=sync_files)
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

def _get_font_latex_config(font_family: str, sync_files: bool = None) -> str:
    """Generate LaTeX font configuration based on font family from text.json.
    
    Args:
        font_family: Font family name from text.json
        sync_files: Whether to sync configuration files
        
    Returns:
        LaTeX commands for font configuration
    """
    from ePy_docs.components.setup import _load_cached_files, _resolve_config_path
    
    try:
        config_path = _resolve_config_path('text', sync_files=sync_files)
        text_config = _load_cached_files(config_path, sync_files=sync_files)
    except Exception:
        text_config = {}
    
    if 'latex_fonts' not in text_config:
        raise ValueError("latex_fonts configuration not found in text.json")
    
    latex_fonts = text_config['latex_fonts']
    
    if font_family not in latex_fonts:
        raise ValueError(f"Font family '{font_family}' not found in text.json latex_fonts")
    
    font_config = latex_fonts[font_family]
    
    if 'package' not in font_config:
        raise ValueError(f"package not found for font '{font_family}' in latex_fonts")
    if 'command' not in font_config:
        raise ValueError(f"command not found for font '{font_family}' in latex_fonts")
    
    return f"\\usepackage{{{font_config['package']}}}\n{font_config['command']}"

def _get_callout_pagebreak_latex_config(sync_files: bool = None) -> str:
    """Generate LaTeX configuration for callout page break control from notes.json.
    
    Args:
        sync_files: Whether to sync configuration files
        
    Returns:
        LaTeX commands for callout page break control
    """
    from ePy_docs.components.setup import _load_cached_files, _resolve_config_path
    
    try:
        config_path = _resolve_config_path('notes', sync_files=sync_files)
        notes_config = _load_cached_files(config_path, sync_files=sync_files)
    except Exception:
        notes_config = {}
    
    if 'pdf_page_break_control' not in notes_config:
        # No page break control configured - return empty
        return ""
    
    break_control = notes_config['pdf_page_break_control']
    
    latex_config = []
    
    # Add penalty configuration for callouts
    if 'latex_page_break_penalties' in break_control:
        penalties = break_control['latex_page_break_penalties']
        
        latex_config.append("% Callout page break control")
        
        # Set penalties to avoid breaking inside callouts
        if 'inside_callout' in penalties:
            inside_penalty = penalties['inside_callout']
            latex_config.append(f"\\widowpenalty={inside_penalty}")
            latex_config.append(f"\\clubpenalty={inside_penalty}")
        
        # Configure callout environment to avoid page breaks
        if break_control.get('avoid_break_inside', False):
            latex_config.extend([
                "% Prevent page breaks inside callouts",
                "\\usepackage{needspace}",
                "\\usepackage{samepage}",
                "",
                "% Redefine callout environments to prevent page breaks",
                "\\let\\originalcallout\\callout",
                "\\let\\originalendcallout\\endcallout",
                "\\renewenvironment{callout}[1][]",
                "{\\begin{samepage}\\originalcallout[#1]}",
                "{\\originalendcallout\\end{samepage}}",
                "",
                "% Alternative approach using mdframed",
                "\\usepackage{mdframed}",
                "\\surroundwithmdframed[nobreak=true]{callout}"
            ])
    
    return "\n".join(latex_config) if latex_config else ""
