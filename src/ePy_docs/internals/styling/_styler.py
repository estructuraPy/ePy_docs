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
from ePy_docs.internals.data_processing._data import _safe_get_nested

def save_txt(content, filepath):
    """Simple text saver fallback"""
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    return filepath

# Import from the page configuration module
from ePy_docs.internals.styling._pages import (
    get_project_config, get_config_value, _ConfigManager,
    get_layout_config, get_header_style, validate_csl_style,
    sync_ref, create_css_styles
)

# Import from COLORS kingdom
from ePy_docs.internals.styling._colors import get_color_from_path

# Color utilities already imported above

def rgb_to_latex_str(rgb_values: List[int]) -> str:
    r"""Convert RGB values to LaTeX color string format.
    
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

from ePy_docs.internals.generation._references import get_default_citation_style
from ePy_docs.internals.styling._colors import get_colors_config

# Import LaTeX helpers from auxiliary module
from ePy_docs.internals.styling._latex_builder import (
    _get_classoptions_for_layout,
    _get_figure_width_for_layout,
    _get_figure_height_for_layout,
    _generate_multicol_config,
    _generate_header_footer_latex,
    _generate_professional_title_page,
    _find_logo_for_layout,
    PDFRenderer,
    _get_font_latex_config,
    _get_callout_pagebreak_latex_config
)

# Note: removed generate_latex_callout_config - now using image-based notes

def _load_config_file(config_type: str = "page") -> Dict[str, Any]:
    """Load configuration file using ConfigManager.
    
    Args:
        config_type: Type of configuration to load ('page' or 'report')
        
    Returns:
        Dict containing the configuration
    """
    valid_types = ["page", "report", "paper"]
    if config_type not in valid_types:
        raise ValueError(f"Invalid config_type '{config_type}'. Must be one of: {valid_types}")
    
    from ePy_docs.config.setup import get_config_section
    
    # Handle special case for 'page' -> 'pages'
    actual_config_type = 'pages' if config_type == 'page' else config_type
    config = get_config_section(actual_config_type)
    
    if not config:
        raise ValueError(f"Configuration section not found: {actual_config_type}")
        
    return config


def generate_quarto_config(layout_name: str = None, document_type: str = "report") -> Dict[str, Any]:
    """Generate Quarto YAML configuration from project settings.
    
    Args:
        layout_name: Layout name to use. If None, uses global current layout.
        document_type: Type of document ("report" or "paper") to determine configuration source.
        
    Returns:
        Dict[str, Any]: Complete Quarto YAML configuration dictionary.
    """
    # Load configuration from pages.json
    page_config = _load_config_file("page")
    
    # Get layout configuration from constitutional realm - report OR paper
    if document_type == "paper":
        config_realm = _load_config_file("paper")
    else:
        config_realm = _load_config_file("report")
    
    # Determine layout_name if not provided
    if layout_name is None:
        # Try to get the current layout first (respects PaperWriter layout_style)
        try:
            from ePy_docs.internals.styling._pages import get_current_layout
            current_layout = get_current_layout()
            layout_name = current_layout
        except:
            # Fallback: Map document types to appropriate default layouts
            if document_type == "paper":
                layout_name = "academic"  # Default academic layout for papers
            else:
                layout_name = "technical"  # Default technical layout for reports
    
    # Load project configuration with constitutional separation
    from ePy_docs.internals.styling._project_info import get_constitutional_project_info, get_project_config_data
    
    # Get constitutional project info based on document type
    constitutional_info = get_constitutional_project_info(document_type)
    project_info = constitutional_info['project']  # Extract project section
    
    # Load full project config for copyright info (still in the old structure for setup.json)
    full_project_config = get_project_config_data()
    copyright_info = constitutional_info.get('copyright', {})
    
    # Get document information - all from constitutional JSON
    title = project_info['name']
    subtitle = project_info['description']
    created_date = project_info['created_date']
    
    # Get all authors from constitutional info
    authors = constitutional_info.get('authors', [])
    
    # Create list of all author names
    if authors:
        author_names = [author['name'] for author in authors]
        # Add the date as the last line
        author_names.append(created_date)
    else:
        author_names = ['Author Name', created_date]
    
    # Get header style from layout
    header_style_from_layout = get_header_style(layout_name)
    
    # Determine CSL style from layout
    citation_style = get_default_citation_style(layout_name)
    csl_file = validate_csl_style(citation_style)
    
    # Get bibliography configuration
    from ePy_docs.internals.generation._references import get_bibliography_config
    from ePy_docs.config.setup import get_current_project_config
    from pathlib import Path
    
    dir_config = get_current_project_config()
    if dir_config is None:
        raise ValueError("No project configuration found.")
        
    bib_config = get_bibliography_config(config=dir_config)
    bib_path = str(bib_config['bibliography']).replace("\\", "/")
    csl_path = str(bib_config['csl']).replace("\\", "/")
    
    styler_config = page_config
    
    # Get crossref configuration from component JSON files, NO FALLBACKS
    from ePy_docs.internals.data_processing._data import load_cached_files
    from ePy_docs.config.setup import _resolve_config_path
    
    # Load configuration for images (for display settings, not crossref)
    try:
        config_path = _resolve_config_path('images')
        images_full_config = load_cached_files(config_path)
        
        # Get layout-specific images configuration
        from ePy_docs.internals.styling._pages import get_layout_config
        layout_config = get_layout_config(layout_name)
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
    
    # Load font configuration from text config using centralized ConfigManager
    from ePy_docs.config.setup import get_config_section
    text_config = get_config_section('text')
    if not text_config:
        raise ValueError("Missing text configuration from master.epyson")
    
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
    
    # Get margins from current layout from constitutional realm instead of pages.json
    if layout_name not in config_realm['layouts']:
        raise ValueError(f"Layout '{layout_name}' not found in {document_type}.json")
    
    current_layout = config_realm['layouts'][layout_name]
    layout_margins = current_layout['margins']
    
    # Convert inches to mm for LaTeX (1 inch = 25.4 mm)
    margin_top_mm = f"{layout_margins['top'] * 25.4:.0f}mm"
    margin_bottom_mm = f"{layout_margins['bottom'] * 25.4:.0f}mm"
    margin_left_mm = f"{layout_margins['left'] * 25.4:.0f}mm"
    margin_right_mm = f"{layout_margins['right'] * 25.4:.0f}mm"
    
    config = {
        'lang': config_realm['project']['lang'],
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
    
    # CONSTITUTIONAL: Add document structure based on type
    if document_type == "report":
        # REPORT format - use standard document (not book) for report style
        config['title'] = title
        config['subtitle'] = subtitle
        config['author'] = author_names
        # Note: No project.type needed for standard document format
    elif document_type == "paper":
        # PAPER format - use individual document structure (no project type for single documents)
        config['title'] = title
        config['subtitle'] = subtitle  
        config['author'] = author_names
    elif document_type == "book":
        # BOOK format - use book structure for multi-chapter documents
        config['project'] = {
            'type': 'book',
            'title': title,
            'subtitle': subtitle,
            'author': author_names
        }
    
    # Get colors for styling based on layout name (header_style_from_layout is now layout name)
    # Get header colors based on the layout's unified layout_styles
    layout_name = header_style_from_layout  # This is now the layout name
    h1_color_rgb = get_color_from_path(f'layout_styles.{layout_name}.typography.h1', format_type="rgb")
    h2_color_rgb = get_color_from_path(f'layout_styles.{layout_name}.typography.h2', format_type="rgb")
    h3_color_rgb = get_color_from_path(f'layout_styles.{layout_name}.typography.h3', format_type="rgb")
    h4_color_rgb = get_color_from_path(f'layout_styles.{layout_name}.typography.h4', format_type="rgb")
    h5_color_rgb = get_color_from_path(f'layout_styles.{layout_name}.typography.h5', format_type="rgb")
    h6_color_rgb = get_color_from_path(f'layout_styles.{layout_name}.typography.h6', format_type="rgb")
    normal_color_rgb = get_color_from_path(f'layout_styles.{layout_name}.typography.normal', format_type="rgb")
    
    # Get header and footer colors from layout_styles
    header_color_rgb = get_color_from_path(f'layout_styles.{layout_name}.typography.header_color', format_type="rgb")
    footer_color_rgb = get_color_from_path(f'layout_styles.{layout_name}.typography.footer_color', format_type="rgb")
    page_number_color_rgb = get_color_from_path(f'layout_styles.{layout_name}.typography.page_number_color', format_type="rgb")
    
    # Get background color for the layout
    try:
        background_color_rgb = get_color_from_path(f'layout_styles.{layout_name}.typography.background_color', format_type="rgb")
    except Exception:
        # Fallback to white background if not defined
        background_color_rgb = [255, 255, 255]
    
    # Also get brand colors for other elements
    primary_blue = get_color_from_path('brand.secondary', format_type="hex")
    accent_red = get_color_from_path('brand.primary', format_type="hex")
    secondary_gray = get_color_from_path('brand.tertiary', format_type="hex")
    
    # Gray scales - all from config
    gray_1 = get_color_from_path('grays_cool.light', format_type="hex")
    gray_2 = get_color_from_path('grays_cool.medium', format_type="hex")
    gray_4 = get_color_from_path('grays_cool.dark', format_type="hex")
    
    # Get page layout configuration for header/footer generation
    page_layout_config = None
    if 'page_layout_key' in current_layout:
        page_layout_key = current_layout['page_layout_key']
        if 'layouts' in page_config and page_layout_key in page_config['layouts']:
            page_layout_config = page_config['layouts'][page_layout_key]
    
    # Generate dynamic header/footer LaTeX based on layout configuration
    # Create project config structure for header/footer function compatibility
    # Include client information from constitutional structure
    client_info = constitutional_info.get('client', {})
    project_config_for_header = {
        'project': project_info, 
        'client': client_info,
        'copyright': copyright_info
    }
    header_footer_latex = _generate_header_footer_latex(
        page_layout_config, 
        project_config_for_header, 
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
{_get_font_latex_config(font_family)}

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

\definecolor{{brandSecondary}}{{RGB}}{{{rgb_to_latex_str(get_color_from_path('brand.secondary', format_type="rgb"))}}}
\definecolor{{Gray_1}}{{RGB}}{{{rgb_to_latex_str(get_color_from_path('grays_cool.light', format_type="rgb"))}}}
\definecolor{{Gray_2}}{{RGB}}{{{rgb_to_latex_str(get_color_from_path('grays_cool.medium', format_type="rgb"))}}}
\definecolor{{Gray_4}}{{RGB}}{{{rgb_to_latex_str(get_color_from_path('grays_cool.dark', format_type="rgb"))}}}

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
{_get_callout_pagebreak_latex_config()}

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

{_generate_multicol_config(layout_name, page_config, images_config)}

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

{_generate_professional_title_page(layout_name, document_type)}
'''
        },
        'documentclass': "article" if document_type == "paper" else "book",
        # Get column count from layout configuration in pages.json
        # IMPORTANT: Only papers (articles) can use two-column layout
        'classoption': _get_classoptions_for_layout(layout_name, page_config, document_type),
        'fontsize': font_size if str(font_size).endswith('pt') else f'{font_size}pt',
        'papersize': merged_pdf_config['papersize'],
        # Margins are already configured via geometry above - removing duplicate hardcoded values
        'linestretch': line_spacing,
        'toc-depth': merged_pdf_config['toc-depth'],
        # Papers (articles) don't have content indices - reports (books) do
        'toc': False if document_type == "paper" else merged_pdf_config['toc'],
        'lof': False if document_type == "paper" else merged_pdf_config['lof'],
        'lot': False if document_type == "paper" else merged_pdf_config['lot'],
        # Figure configurations from images.json - adjusted for column layout
        'fig-width': _get_figure_width_for_layout(layout_name, page_config, images_config),
        'fig-height': _get_figure_height_for_layout(layout_name, page_config, images_config),
        'fig-pos': merged_pdf_config['fig-pos'],
        'fig-cap-location': merged_pdf_config['fig-cap-location'],
        'colorlinks': merged_pdf_config.get('colorlinks', False)
    }
    
    # Filter out None values to prevent YAML null issues that cause Quarto errors
    pdf_config = {k: v for k, v in pdf_config.items() if v is not None}
    
    # Create HTML format configuration - NO FALLBACKS, read from component configs
    if 'html' not in styler_config['format']:
        raise ValueError("Missing 'html' section in format configuration")
    
    html_format_config = styler_config['format']['html']
    
    # Merge common and HTML-specific configurations
    merged_html_config = {**common_config, **html_format_config}
    
    html_config = {
        'theme': merged_html_config['theme'],
        'css': 'styles.css',  # Add CSS reference
        # Papers (articles) don't have table of contents - reports (books) do
        'toc': False if document_type == "paper" else merged_html_config['toc'],
        'toc-depth': merged_html_config['toc-depth'],
        'number-sections': merged_html_config['number-sections'],
        'html-math-method': 'mathjax',
        'self-contained': merged_html_config['self-contained'],
        'embed-resources': merged_html_config['embed-resources'],
        # Figure configurations from images.json - adjusted for two-column papers
        'fig-width': _safe_get_nested(images_config, 'display.two_column_layout.html.max_width_inches', 4.0) if document_type == "paper" else _safe_get_nested(images_config, 'display.max_width_inches_html', 7),
        'fig-height': (_safe_get_nested(images_config, 'display.two_column_layout.html.max_width_inches', 4.0) * 0.6) if document_type == "paper" else (_safe_get_nested(images_config, 'display.max_width_inches_html', 7) * 0.6),
        'fig-align': _safe_get_nested(images_config, 'styling.alignment', 'center').lower(),
        'fig-responsive': _safe_get_nested(images_config, 'display.html_responsive', True),
        'fig-cap-location': merged_html_config['fig-cap-location'],
        'tbl-cap-location': merged_html_config['tbl-cap-location'],
        'fig-dpi': _safe_get_nested(images_config, 'display.dpi', 300) // 2,  # Half DPI for HTML
        'code-fold': merged_html_config['code-fold'],
        'code-tools': merged_html_config['code-tools']
    }
    
    # Add format configurations to main config
    config['format'] = {
        'pdf': pdf_config,
        'html': html_config
    }
    
    return config

def create_quarto_yml(output_dir: str, chapters: Optional[List[str]] = None, document_type: str = "report") -> str:
    """Create _quarto.yml file from project configuration.
    
    Args:
        output_dir: Directory where the _quarto.yml file will be created.
        chapters: Optional list of chapter paths to include in the configuration.
        document_type: Type of document ("report" or "paper"). Defaults to "report".
        
    Returns:
        str: Absolute path to the created _quarto.yml file.
    """
    config = generate_quarto_config(document_type=document_type)
    
    if chapters:
        config['book']['chapters'] = chapters
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    config_file = output_path / "_quarto.yml"
    try:
        # Usar ePy_files directamente
        import yaml
        yaml_content = yaml.dump(config, default_flow_style=False, sort_keys=False, allow_unicode=True)
        save_txt(yaml_content, config_file)
    except Exception as e:
        raise RuntimeError(f"Failed to write Quarto configuration file: {e}")
    
    css_file = output_path / "styles.css"
    from ePy_docs.internals.styling._pages import get_current_layout
    current_layout = get_current_layout()
    css_content = create_css_styles(layout_name=current_layout)
    try:
        # Usar ePy_files directamente
        save_txt(css_content, css_file)
    except Exception as e:
        raise RuntimeError(f"Failed to write CSS file: {e}")
    
    return str(config_file)

def create_quarto_project(output_dir: str, 
                         chapters: Optional[List[str]] = None,
                         create_index: bool = True,
                         document_type: str = "report") -> Dict[str, str]:
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
        document_type: Type of document ("report" or "paper"). Defaults to "report".
        
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
        document_type=document_type
    )
    created_files['quarto_yml'] = quarto_yml_path
    
    # 2. CSS file is already created by create_quarto_yml
    css_path = output_path / "styles.css"
    created_files['styles_css'] = str(css_path.absolute())
    
    # 3. Create index.qmd if requested
    if create_index:
        index_content = create_index_qmd(document_type=document_type)
        index_path = output_path / "index.qmd"
        
        try:
            # Usar ePy_files directamente
            save_txt(index_content, index_path)
        except Exception as e:
            raise RuntimeError(f"Failed to write index.qmd file: {e}")
        
        created_files['index_qmd'] = str(index_path.absolute())
    
    return created_files

def create_index_qmd(document_type: str = "report") -> str:
    """Create content for an index.qmd file based on project configuration.
    
    Args:
        document_type: Type of document ("report" or "paper")
        
    Returns:
        str: Complete content for index.qmd file.
        
    Raises:
        FileNotFoundError: If project.json file doesn't exist.
        KeyError: If required keys are missing from configuration.
        JSONDecodeError: If JSON file is malformed.
    """
    from ePy_docs.internals.styling._project_info import get_constitutional_project_info
    from ePy_docs.config.setup import _load_cached_config
    
    # Read constitutional project configuration
    project_info = get_constitutional_project_info(document_type)
    
    # Get full project data for consultants info (still in main structure)
    project_data = _load_cached_config('project_info')
    if not project_data:
        raise ValueError("Missing project configuration from project_info.json")
    
    # Extract project information - using constitutional data
    title = project_info['name']
    description = project_info['description']
    version = project_info['version']
    code = project_info['code']
    created_date = project_info['created_date']
    
    # Extract author information from common data
    authors = project_data.get('common', {}).get('authors', project_data.get('authors', []))
    author = authors[0]['name']
    author_specialty = authors[0]['specialty']
    author_license = authors[0]['license']
    
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

